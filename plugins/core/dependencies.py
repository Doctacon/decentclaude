"""
Plugin dependency resolution and ordering.

Resolves plugin dependencies and determines the correct loading order
to ensure dependencies are loaded before plugins that depend on them.
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict, deque


class DependencyError(Exception):
    """Raised when dependency resolution fails"""
    pass


class CircularDependencyError(DependencyError):
    """Raised when circular dependencies are detected"""
    pass


class MissingDependencyError(DependencyError):
    """Raised when a required dependency is not available"""
    pass


class DependencyResolver:
    """Resolves plugin dependencies and determines load order"""

    def __init__(self):
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.available_plugins: Set[str] = set()

    def add_plugin(self, plugin_name: str, dependencies: List[str]) -> None:
        """
        Add a plugin and its dependencies to the resolver.

        Args:
            plugin_name: Name of the plugin
            dependencies: List of plugin names this plugin depends on
        """
        self.available_plugins.add(plugin_name)
        self.dependency_graph[plugin_name] = dependencies

    def resolve(self) -> List[str]:
        """
        Resolve dependencies and return plugins in load order.

        Returns:
            List of plugin names in the order they should be loaded

        Raises:
            CircularDependencyError: If circular dependencies are detected
            MissingDependencyError: If required dependencies are missing
        """
        self._validate_dependencies()

        visited: Set[str] = set()
        temp_mark: Set[str] = set()
        load_order: List[str] = []

        def visit(node: str) -> None:
            """Depth-first search for topological sort"""
            if node in temp_mark:
                raise CircularDependencyError(
                    f"Circular dependency detected involving plugin: {node}"
                )

            if node not in visited:
                temp_mark.add(node)

                for dep in self.dependency_graph.get(node, []):
                    visit(dep)

                temp_mark.remove(node)
                visited.add(node)
                load_order.append(node)

        for plugin in self.available_plugins:
            if plugin not in visited:
                visit(plugin)

        return load_order

    def _validate_dependencies(self) -> None:
        """
        Validate that all dependencies are available.

        Raises:
            MissingDependencyError: If required dependencies are missing
        """
        for plugin_name, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep not in self.available_plugins:
                    raise MissingDependencyError(
                        f"Plugin '{plugin_name}' requires '{dep}' which is not available"
                    )

    def get_dependencies(self, plugin_name: str, recursive: bool = False) -> List[str]:
        """
        Get dependencies for a plugin.

        Args:
            plugin_name: Name of the plugin
            recursive: If True, get all transitive dependencies

        Returns:
            List of dependency names
        """
        if not recursive:
            return self.dependency_graph.get(plugin_name, [])

        visited: Set[str] = set()
        result: List[str] = []

        def collect_deps(name: str) -> None:
            """Recursively collect dependencies"""
            if name in visited:
                return

            visited.add(name)
            for dep in self.dependency_graph.get(name, []):
                collect_deps(dep)
                if dep not in result:
                    result.append(dep)

        collect_deps(plugin_name)
        return result

    def get_dependents(self, plugin_name: str) -> List[str]:
        """
        Get plugins that depend on this plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            List of plugin names that depend on this plugin
        """
        dependents = []
        for name, deps in self.dependency_graph.items():
            if plugin_name in deps:
                dependents.append(name)
        return dependents

    def can_unload(self, plugin_name: str) -> bool:
        """
        Check if a plugin can be safely unloaded.

        A plugin can be unloaded if no other loaded plugins depend on it.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if plugin can be unloaded, False otherwise
        """
        dependents = self.get_dependents(plugin_name)
        return len(dependents) == 0

    def get_unload_order(self, plugins_to_unload: List[str]) -> List[str]:
        """
        Get the order in which plugins should be unloaded.

        Plugins are unloaded in reverse dependency order.

        Args:
            plugins_to_unload: List of plugin names to unload

        Returns:
            List of plugin names in unload order
        """
        subgraph = DependencyResolver()
        for plugin in plugins_to_unload:
            deps = [d for d in self.dependency_graph.get(plugin, []) if d in plugins_to_unload]
            subgraph.add_plugin(plugin, deps)

        load_order = subgraph.resolve()
        return list(reversed(load_order))


class DependencyTree:
    """Represents a dependency tree for visualization"""

    def __init__(self, resolver: DependencyResolver):
        self.resolver = resolver

    def print_tree(self, plugin_name: str, prefix: str = "", is_last: bool = True) -> str:
        """
        Generate a visual tree representation of dependencies.

        Args:
            plugin_name: Root plugin name
            prefix: Prefix for tree drawing (used internally)
            is_last: Whether this is the last child (used internally)

        Returns:
            String representation of the dependency tree
        """
        tree = []
        connector = "└── " if is_last else "├── "
        tree.append(prefix + connector + plugin_name)

        dependencies = self.resolver.dependency_graph.get(plugin_name, [])
        extension = "    " if is_last else "│   "

        for i, dep in enumerate(dependencies):
            is_last_dep = i == len(dependencies) - 1
            tree.append(self.print_tree(dep, prefix + extension, is_last_dep))

        return "\n".join(tree)

    def get_full_tree(self) -> str:
        """
        Get dependency tree for all plugins.

        Returns:
            String representation of all dependency trees
        """
        roots = []
        all_deps = set()

        for plugin, deps in self.resolver.dependency_graph.items():
            all_deps.update(deps)

        roots = [p for p in self.resolver.available_plugins if p not in all_deps]

        if not roots:
            roots = list(self.resolver.available_plugins)

        trees = []
        for root in roots:
            trees.append(self.print_tree(root, "", True))

        return "\n\n".join(trees)
