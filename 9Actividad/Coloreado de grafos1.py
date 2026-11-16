import sys
from time import perf_counter_ns


class Graph:
	def __init__(self, name="Grafo vacío"):
		self.name = name
		self.adjacency = {}

	def add_vertex(self, vertex):
		if vertex in self.adjacency:
			return False
		self.adjacency[vertex] = set()
		return True

	def remove_vertex(self, vertex):
		if vertex not in self.adjacency:
			return False
		for neighbor in self.adjacency[vertex]:
			self.adjacency[neighbor].remove(vertex)
		del self.adjacency[vertex]
		return True

	def add_edge(self, first, second):
		if first not in self.adjacency or second not in self.adjacency:
			return "missing"
		if first == second:
			return "loop"
		if second in self.adjacency[first]:
			return "duplicate"
		self.adjacency[first].add(second)
		self.adjacency[second].add(first)
		return "added"

	def degree(self, vertex):
		return len(self.adjacency[vertex])

	def edge_count(self):
		return sum(map(len, self.adjacency.values())) // 2

	def copy(self):
		duplicate = Graph(self.name)
		duplicate.adjacency = {v: set(neighbors) for v, neighbors in self.adjacency.items()}
		return duplicate


def example_graph():
	graph = Graph("Ejemplo general")
	for vertex in "ABCDEFGH":
		graph.add_vertex(vertex)
	edges = [
		("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"),
		("B", "C"), ("B", "F"), ("C", "D"), ("C", "F"),
		("D", "E"), ("D", "G"), ("E", "G"), ("E", "H"),
		("F", "G"), ("F", "H"), ("G", "H"),
	]
	for first, second in edges:
		graph.add_edge(first, second)
	return graph


def available_color(graph, vertex, colors):
	neighbor_colors = {colors[n] for n in graph.adjacency[vertex] if n in colors}
	color = 1
	while color in neighbor_colors:
		color += 1
	return color


def make_step(graph, colors, vertex, reason, saturation=None, saturation_after=None):
	neighbor_colors = {
		neighbor: colors[neighbor]
		for neighbor in graph.adjacency[vertex]
		if neighbor in colors
	}
	return {
		"vertex": vertex,
		"reason": reason,
		"degree": graph.degree(vertex),
		"saturation": saturation,
		"neighbor_colors": neighbor_colors,
		"color": colors[vertex],
		"state": dict(colors),
		"saturation_after": saturation_after,
	}


def saturation_degrees(graph, colors):
	return {
		vertex: len({colors[n] for n in graph.adjacency[vertex] if n in colors})
		for vertex in graph.adjacency
		if vertex not in colors
	}


def greedy_coloring(graph):
	colors, steps = {}, []
	order = list(graph.adjacency)
	for vertex in order:
		colors[vertex] = available_color(graph, vertex, colors)
		steps.append(make_step(
			graph, colors, vertex,
			"Orden de creación (recorrido voraz); se usa el menor color disponible.",
		))
	return result("Voraz", colors, steps, order, 0)


def welsh_powell_coloring(graph):
	colors, steps = {}, []
	order_index = {vertex: i for i, vertex in enumerate(graph.adjacency)}
	order = sorted(graph.adjacency, key=lambda v: (-graph.degree(v), order_index[v]))
	passes = 0
	while len(colors) < len(graph.adjacency):
		passes += 1
		color = passes
		group = []
		for vertex in order:
			if vertex in colors:
				continue
			if all(neighbor not in group for neighbor in graph.adjacency[vertex]):
				colors[vertex] = color
				group.append(vertex)
				steps.append(make_step(
					graph, colors, vertex,
					"Mayor grado primero; desempate por orden de creación. "
					"Se incorpora al grupo actual porque no es adyacente a él.",
				))
	return result("Welsh-Powell", colors, steps, [s["vertex"] for s in steps], passes)


def dsatur_coloring(graph):
	colors, steps = {}, []
	order_index = {vertex: i for i, vertex in enumerate(graph.adjacency)}
	order = []
	while len(colors) < len(graph.adjacency):
		saturation = saturation_degrees(graph, colors)
		uncolored = [v for v in graph.adjacency if v not in colors]
		if not colors:
			vertex = min(uncolored, key=lambda v: (-graph.degree(v), order_index[v]))
			reason = "Selección inicial: mayor grado total; desempate por orden de creación."
		else:
			vertex = min(
				uncolored,
				key=lambda v: (-saturation[v], -graph.degree(v), order_index[v]),
			)
			reason = (
				"Mayor saturación (" + str(saturation[vertex]) + "); "
				"desempate por mayor grado total y luego orden de creación."
			)
		colors[vertex] = available_color(graph, vertex, colors)
		order.append(vertex)
		after = saturation_degrees(graph, colors)
		steps.append(make_step(
			graph, colors, vertex, reason, saturation[vertex], after,
		))
	return result("DSatur", colors, steps, order, 0)


def result(name, colors, steps, order, passes):
	return {
		"name": name,
		"colors": colors,
		"steps": steps,
		"order": order,
		"color_count": len(set(colors.values())),
		"iterations": len(steps),
		"passes": passes,
	}


def is_valid_coloring(graph, colors):
	return all(
		vertex in colors and neighbor in colors and colors[vertex] != colors[neighbor]
		for vertex, neighbors in graph.adjacency.items()
		for neighbor in neighbors
	)


ALGORITHMS = {
	"Voraz": greedy_coloring,
	"Welsh-Powell": welsh_powell_coloring,
	"DSatur": dsatur_coloring,
}


def show_graph(graph):
	vertices = list(graph.adjacency)
	print("\nGrafo:", graph.name)
	print("Vértices:", ", ".join(vertices) if vertices else "(ninguno)")
	edges = [(v, n) for i, v in enumerate(vertices)
			 for n in vertices[i + 1:] if n in graph.adjacency[v]]
	print("Aristas:", ", ".join(f"({a}, {b})" for a, b in edges) if edges else "(ninguna)")
	print("Matriz de adyacencia:")
	if not vertices:
		print("(vacía)")
		return
	print("    " + " ".join(f"{v:>3}" for v in vertices))
	for vertex in vertices:
		row = " ".join(f"{int(n in graph.adjacency[vertex]):>3}" for n in vertices)
		print(f"{vertex:>3} {row}")


def display_result(graph, outcome):
	print(f"\n=== {outcome['name']} ===")
	shown = outcome["steps"][:6]
	if not shown:
		print("El grafo no tiene vértices; no se requieren colores.")
	for index, step in enumerate(shown, 1):
		print(f"\nPASO {index} - {outcome['name']}")
		print(f"Vértice seleccionado: {step['vertex']}")
		print(f"Grado: {step['degree']}")
		if step["saturation"] is not None:
			print(f"Grado de saturación: {step['saturation']}")
		print("Criterio:", step["reason"])
		neighbor_colors = step["neighbor_colors"]
		print("Colores de vecinos ya coloreados:",
			  ", ".join(f"{v}=Color {c}" for v, c in neighbor_colors.items()) or "ninguno")
		print(f"Color asignado: Color {step['color']}")
		print("Estado parcial:")
		for vertex in graph.adjacency:
			color = step["state"].get(vertex)
			print(f"  {vertex} -> Color {color}" if color else f"  {vertex} -> Sin colorear")
		if step["saturation_after"] is not None and step["saturation_after"]:
			detail = ", ".join(f"{v}={value}" for v, value in step["saturation_after"].items())
			print("Saturación actualizada (vértices sin colorear):", detail)
	if len(outcome["steps"]) > 6:
		print(f"\nSe muestran 6 de {len(outcome['steps'])} pasos; el algoritmo continuó "
			  "internamente hasta completar el grafo.")
	print("\nOrden de selección:", " -> ".join(outcome["order"]) or "(ninguno)")
	if outcome["name"] == "Welsh-Powell":
		print("Grados:", ", ".join(f"{v}={graph.degree(v)}" for v in graph.adjacency) or "(ninguno)")
		print("Orden descendente:", " -> ".join(sorted(
			graph.adjacency, key=lambda v: (-graph.degree(v), list(graph.adjacency).index(v))
		)) or "(ninguno)")
		for color in range(1, outcome["color_count"] + 1):
			group = [v for v in outcome["order"] if outcome["colors"][v] == color]
			print(f"Grupo Color {color}:", ", ".join(group))
		print("Pasadas/grupos de color:", outcome["passes"])
	if outcome["name"] == "DSatur":
		print("Grados:", ", ".join(f"{v}={graph.degree(v)}" for v in graph.adjacency) or "(ninguno)")
	print("Coloreado final:", ", ".join(
		f"{v}=Color {outcome['colors'][v]}" for v in graph.adjacency
	) or "(ninguno)")
	print("Colores utilizados:", outcome["color_count"])
	print("Coloreado válido:", "Sí" if is_valid_coloring(graph, outcome["colors"]) else "No")
	print("Nota: es una solución heurística válida (cota superior), no necesariamente el número cromático exacto.")


def run_algorithm(graph, name, show=True):
	outcome = ALGORITHMS[name](graph.copy())
	if show:
		display_result(graph, outcome)
	return outcome


def compare_results(graph):
	measured = []
	for name, algorithm in ALGORITHMS.items():
		graph_copy = graph.copy()
		start = perf_counter_ns()
		outcome = algorithm(graph_copy)
		elapsed_ms = (perf_counter_ns() - start) / 1_000_000
		measured.append((outcome, elapsed_ms, is_valid_coloring(graph_copy, outcome["colors"])))

	best = min((item[0]["color_count"] for item in measured), default=0)
	fastest = min(measured, key=lambda item: item[1]) if measured else None
	print("\n=== Comparación ===")
	print(f"{'Parámetro':<30}" + "".join(f"{name:>19}" for name in ALGORITHMS))
	print("-" * 87)
	rows = [
		("Colores utilizados", lambda o, t, valid: str(o["color_count"])),
		("Coloreado válido", lambda o, t, valid: "Sí" if valid else "No"),
		("Tiempo (ms)", lambda o, t, valid: f"{t:.6f}"),
		("Iteraciones (vértices)", lambda o, t, valid: str(o["iterations"])),
		("Pasadas / grupos", lambda o, t, valid: str(o["passes"] if o["name"] == "Welsh-Powell" else "—")),
		("Exceso de colores (%)", lambda o, t, valid: f"{((o['color_count'] - best) / best * 100):.1f}%" if best else "0.0%"),
		("Orden de selección", lambda o, t, valid: " → ".join(o["order"]) or "(ninguno)"),
	]
	for label, formatter in rows:
		print(f"{label:<30}" + "".join(f"{formatter(o, t, valid):>19}" for o, t, valid in measured))
	if not measured:
		return
	best_names = [o["name"] for o, _, _ in measured if o["color_count"] == best]
	fastest_names = [o["name"] for o, t, _ in measured if t == fastest[1]]
	print("\nMenos colores:", ", ".join(best_names), "(" + str(best) + ")")
	print("Menor tiempo:", ", ".join(fastest_names), f"({fastest[1]:.6f} ms)")
	print("Calidad:", "hubo diferencias entre algoritmos." if len({o['color_count'] for o, _, _ in measured}) > 1
		  else "los tres empataron en cantidad de colores.")
	balanced = min(measured, key=lambda item: (item[0]["color_count"], item[1]))[0]["name"]
	print("Mejor equilibrio (menos colores y, en empate, menor tiempo):", balanced)
	print("Los resultados heurísticos son coloreados válidos y cotas superiores; no garantizan el número cromático exacto.")


def read_vertex(prompt):
	return input(prompt).strip()


def menu():
	graph = Graph()
	while True:
		print("\n" + "=" * 55)
		print(f"Grafo actual: {graph.name}")
		print(f"Número de vértices: {len(graph.adjacency)}")
		print(f"Número de aristas: {graph.edge_count()}")
		print("\n1. Cargar grafo ejemplo (General)\n2. Crear vértice\n3. Eliminar vértice\n"
			  "4. Crear arista\n5. Algoritmo Voraz\n6. Algoritmo Welsh-Powell\n"
			  "7. Algoritmo DSatur\n8. Comparar resultados\n9. Salir")
		try:
			choice = input("Seleccione una opción: ").strip()
		except (EOFError, KeyboardInterrupt):
			print("\nHasta luego.")
			return
		if choice == "1":
			graph = example_graph()
			show_graph(graph)
		elif choice == "2":
			vertex = read_vertex("Identificador del nuevo vértice: ")
			if not vertex:
				print("El identificador no puede estar vacío.")
			elif graph.add_vertex(vertex):
				graph.name = "Grafo personalizado"
				print(f"Vértice {vertex} agregado.")
			else:
				print("Ese vértice ya existe.")
		elif choice == "3":
			vertex = read_vertex("Vértice que desea eliminar: ")
			if graph.remove_vertex(vertex):
				graph.name = "Grafo personalizado"
				print(f"Vértice {vertex} y sus aristas fueron eliminados.")
			else:
				print("El vértice no existe.")
		elif choice == "4":
			first = read_vertex("Primer vértice: ")
			second = read_vertex("Segundo vértice: ")
			status = graph.add_edge(first, second)
			messages = {
				"added": "Arista agregada.", "missing": "Ambos vértices deben existir.",
				"loop": "No se permiten bucles.", "duplicate": "La arista ya existe.",
			}
			if status == "added":
				graph.name = "Grafo personalizado"
			print(messages[status])
		elif choice in ("5", "6", "7"):
			names = {"5": "Voraz", "6": "Welsh-Powell", "7": "DSatur"}
			run_algorithm(graph, names[choice])
		elif choice == "8":
			compare_results(graph)
		elif choice == "9":
			print("Hasta luego.")
			return
		else:
			print("Opción no válida; seleccione un número del 1 al 9.")


def run_self_tests():
	"""Pruebas rápidas de validez para los casos principales solicitados."""
	cases = []
	cases.append(Graph("vacío"))
	one = Graph("un vértice")
	one.add_vertex("A")
	cases.append(one)
	isolated = Graph("sin aristas")
	for vertex in "ABC":
		isolated.add_vertex(vertex)
	cases.append(isolated)
	complete = Graph("completo")
	for vertex in "ABCD":
		complete.add_vertex(vertex)
	for i, first in enumerate(complete.adjacency):
		for second in list(complete.adjacency)[i + 1:]:
			complete.add_edge(first, second)
	cases.append(complete)
	bipartite = Graph("bipartito")
	for vertex in "ABCD":
		bipartite.add_vertex(vertex)
	for edge in [("A", "C"), ("A", "D"), ("B", "C"), ("B", "D")]:
		bipartite.add_edge(*edge)
	cases.append(bipartite)
	cycle = Graph("ciclo")
	for vertex in "ABCDE":
		cycle.add_vertex(vertex)
	for edge in [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A")]:
		cycle.add_edge(*edge)
	cases.append(cycle)
	modified = Graph("personalizado")
	for vertex in "ABC":
		modified.add_vertex(vertex)
	modified.add_edge("A", "B")
	modified.add_edge("B", "C")
	modified.remove_vertex("C")
	cases.append(modified)
	cases.append(example_graph())
	for graph in cases:
		for algorithm in ALGORITHMS.values():
			outcome = algorithm(graph.copy())
			assert len(outcome["colors"]) == len(graph.adjacency)
			assert is_valid_coloring(graph, outcome["colors"])
	print(f"Pruebas correctas: {len(cases)} grafos y {len(cases) * len(ALGORITHMS)} ejecuciones.")


if __name__ == "__main__":
	if "--test" in sys.argv:
		run_self_tests()
	else:
		menu()
