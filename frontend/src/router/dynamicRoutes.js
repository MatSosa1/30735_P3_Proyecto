import UsersListView from '../views/users/UsersListView.vue'
import RolesListView from '../views/roles/RolesListView.vue'
import ModulesListView from '../views/modules/ModulesListView.vue'
import PlaceholderView from '../views/PlaceholderView.vue'

// El backend decide QUÉ rutas existen (GET /menus/tree, según el rol); esto solo resuelve CON
// QUÉ componente se renderiza una url_module ya conocida por el cliente. Cualquier url_module
// que no esté en este mapa (ej. los items de demo del seed, '/item1'...) cae a un placeholder
// en vez de romper — nunca se hardcodea la navegación en sí, solo el renderer de lo conocido.
const KNOWN_MODULE_COMPONENTS = {
  '/users': UsersListView,
  '/roles': RolesListView,
  '/modules': ModulesListView,
}

function collectLeaves(nodes, leaves = []) {
  for (const node of nodes) {
    if (node.url_module) {
      leaves.push(node)
    }

    if (node.children?.length) {
      collectLeaves(node.children, leaves)
    }
  }

  return leaves
}

export function registerDynamicRoutes(router, tree) {
  const leaves = collectLeaves(tree)

  for (const leaf of leaves) {
    const path = leaf.url_module.replace(/^\/+/, '')

    if (!path) continue

    router.addRoute('app', {
      path,
      name: `module-${leaf.id_module}`,
      component: KNOWN_MODULE_COMPONENTS[leaf.url_module] ?? PlaceholderView,
      props: KNOWN_MODULE_COMPONENTS[leaf.url_module]
        ? undefined
        : { title: leaf.name_module },
      meta: { moduleId: leaf.id_module },
    })
  }
}
