from typing import Any, Optional, TypeVar

from .expression import Expression


T = TypeVar("T")

def get_print_width(x: Expression[Any], indent: int) -> int:
    if x.has_children:
        return max(
            len(x.rootname),
            indent + max(
                get_print_width(child, indent=indent)
                for child in x.children
            )
        )
    return len(x.rootname)

def resolve(
        x: Expression[T],
        prefix: str = "",
        indent: str = " ",
        width: Optional[int] = None,
) -> T:
    if width is None:
        width = len(prefix) + get_print_width(x, indent=1+len(indent))

    if x.has_children:
        print(prefix + "\u250c\u2500")

    if len(x.left_children) > 0:
        child_prefix = prefix + ("\u2524" if x.is_infix else "\u2502") + indent
        for child in x.left_children:
            resolve(
                child,
                prefix=child_prefix,
                indent=indent,
                width=width,
            )

    if x.is_infix:
        print(prefix + "\u255e\u2550")

    if len(x.right_children) > 0:
        child_prefix = prefix + ("\u251c" if x.is_infix else "\u2502") + indent
        for child in x.right_children:
            resolve(
                child,
                prefix=child_prefix,
                indent=indent,
                width=width,
            )

    if x.has_children:
        print(prefix + "\u251c\u2500")

    try:
        lines = repr(x.get()).splitlines()
        print(f"{(prefix + x.rootname).ljust(width)}  = {lines[0]}")
        for line in lines[1:]:
            print(f"{prefix.ljust(width + 4)}{line}")
    except Exception as e:
        print(f"{(prefix + x.rootname).ljust(width)}  ERROR: {e}")
        raise
    return x.get()
