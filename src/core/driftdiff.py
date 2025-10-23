"""Detect drift between source code AST signatures and documented contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional
import ast


@dataclass
class FunctionSignature:
    """Representation of a function or method signature."""

    name: str
    args: List[str]
    vararg: bool
    kwarg: bool
    kwonly: List[str]
    returns: Optional[str]

    @classmethod
    def from_function_def(cls, node: ast.AST) -> "FunctionSignature":
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise TypeError("Expected a function definition node")
        args = [arg.arg for arg in node.args.args]
        kwonly = [arg.arg for arg in node.args.kwonlyargs]
        returns = _annotation_to_str(node.returns)
        return cls(
            name=node.name,
            args=args,
            vararg=node.args.vararg is not None,
            kwarg=node.args.kwarg is not None,
            kwonly=kwonly,
            returns=returns,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "args": list(self.args),
            "vararg": self.vararg,
            "kwarg": self.kwarg,
            "kwonly": list(self.kwonly),
            "returns": self.returns,
        }


def _annotation_to_str(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = _annotation_to_str(node.value)
        return f"{value}.{node.attr}" if value else node.attr
    if isinstance(node, ast.Subscript):
        return f"{_annotation_to_str(node.value)}[{_annotation_to_str(node.slice)}]"
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if hasattr(ast, "unparse"):
        return ast.unparse(node)
    return None


def parse_signatures(path: str | Path) -> Dict[str, FunctionSignature]:
    """Return function signatures defined at module top level."""

    module_path = Path(path)
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(module_path))
    signatures: Dict[str, FunctionSignature] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = FunctionSignature.from_function_def(node)
            signatures[sig.name] = sig
    return signatures


def _expected_functions(contract: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    if "functions" in contract:
        funcs = contract["functions"]
        if isinstance(funcs, Mapping):
            return {str(k): v for k, v in funcs.items() if isinstance(v, Mapping)}
    io = contract.get("io") if isinstance(contract, Mapping) else None
    if isinstance(io, Mapping):
        funcs = io.get("functions")
        if isinstance(funcs, Mapping):
            return {str(k): v for k, v in funcs.items() if isinstance(v, Mapping)}
    return {}


def _expected_args(expected: Mapping[str, Any]) -> List[str]:
    if "args" in expected and isinstance(expected["args"], Iterable):
        return [str(arg) for arg in expected["args"]]
    inputs = expected.get("inputs") if isinstance(expected, Mapping) else None
    if isinstance(inputs, Mapping):
        return [str(name) for name in inputs.keys()]
    if isinstance(inputs, Iterable):
        return [str(name) for name in inputs]
    return []


def _expected_return(expected: Mapping[str, Any]) -> Optional[str]:
    if "returns" in expected:
        value = expected["returns"]
        if isinstance(value, Mapping):
            return str(value.get("type")) if value.get("type") is not None else None
        return str(value)
    outputs = expected.get("outputs") if isinstance(expected, Mapping) else None
    if isinstance(outputs, Mapping) and outputs:
        return ",".join(sorted(str(name) for name in outputs.keys()))
    if isinstance(outputs, Iterable):
        return ",".join(sorted(str(name) for name in outputs))
    return None


def compare_contract(path: str | Path, contract: Mapping[str, Any]) -> Dict[str, Any]:
    """Compare signatures with contract expectations.

    Parameters
    ----------
    path:
        Module file to inspect.
    contract:
        Parsed `.purpose.md` contract converted into a dictionary. Only the
        `functions` or `io.functions` sections are inspected. Each function may
        declare optional `inputs`/`args` and `outputs`/`returns` entries.
    """

    actual = parse_signatures(path)
    expected = _expected_functions(contract)

    matches: List[Dict[str, Any]] = []
    mismatches: List[Dict[str, Any]] = []
    missing: List[str] = []
    unexpected: List[str] = []

    for name, spec in expected.items():
        signature = actual.get(name)
        if signature is None:
            missing.append(name)
            continue
        expected_args = _expected_args(spec)
        expected_return = _expected_return(spec)
        differences: Dict[str, Any] = {}
        if expected_args and expected_args != signature.args:
            differences["args"] = {"expected": expected_args, "actual": signature.args}
        if expected_return and expected_return != signature.returns:
            differences["returns"] = {"expected": expected_return, "actual": signature.returns}
        if differences:
            entry = {"name": name, **differences}
            mismatches.append(entry)
        else:
            matches.append(signature.to_dict())

    for name in set(actual) - set(expected):
        unexpected.append(name)

    return {
        "matches": matches,
        "mismatches": mismatches,
        "missing": missing,
        "unexpected": unexpected,
        "inspected_file": str(path),
    }


__all__ = ["FunctionSignature", "parse_signatures", "compare_contract"]
