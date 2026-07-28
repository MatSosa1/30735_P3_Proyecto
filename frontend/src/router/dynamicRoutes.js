import ModulesListView from "../views/modules/ModulesListView.vue";
import PlaceholderView from "../views/PlaceholderView.vue";
import RolesListView from "../views/roles/RolesListView.vue";
import UsersListView from "../views/users/UsersListView.vue";

const KNOWN_MODULE_COMPONENTS = {
    "/users": UsersListView,
    "/roles": RolesListView,
    "/modules": ModulesListView,
};

function collectLeaves(nodes, leaves = []) {
    for (const node of nodes) {
        if (node.url_module) {
            leaves.push(node);
        }

        if (node.children?.length) {
            collectLeaves(node.children, leaves);
        }
    }

    return leaves;
}

function isExternalUrl(url) {
    return !url.startsWith("/");
}

export function registerDynamicRoutes(router, tree) {
    const leaves = collectLeaves(tree);

    for (const leaf of leaves) {
        if (isExternalUrl(leaf.url_module)) continue;

        const path = leaf.url_module.replace(/^\/+/, "");

        if (!path) continue;

        router.addRoute("app", {
            path,
            name: `module-${leaf.id_module}`,
            component: KNOWN_MODULE_COMPONENTS[leaf.url_module] ?? PlaceholderView,
            props: KNOWN_MODULE_COMPONENTS[leaf.url_module] ? undefined : { title: leaf.name_module },
            meta: { moduleId: leaf.id_module },
        });
    }
}
