from typing import Optional

from pydantic._internal._model_construction import ModelMetaclass


class AllOptional(ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = dict(namespaces.get("__annotations__", {}))
        # Merge base annotations
        for base in bases:
            base_ann = getattr(base, "__annotations__", {})
            if base_ann:
                annotations.update(base_ann)
        # Mark all fields Optional and set default=None when not explicitly set
        for field in list(annotations.keys()):
            if field.startswith("__"):
                continue
            annotations[field] = Optional[annotations[field]]
            # If a default isn't already provided, set it to None so field is not required
            if field not in namespaces:
                namespaces[field] = None
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)
