package day16

import (
	"adventOfCode2023/helpers"
	"log"
	"strconv"
	"strings"
)

func Solve(inputLines []string) (int, int) {
	return partOne(inputLines), 0
}

func partOne(inputLines []string) int {
	const TIME_LIMIT int = 30
	network := buildNetwork(inputLines)
	path := []Tunnel{}
	estimate, _ := network.evaluatePath(path, TIME_LIMIT)
	plans := []Plan{{path: path, estimate: estimate}}
	var bestPlan Plan
	for {
		candidate := plans[len(plans)-1]
		plans = plans[:len(plans)-1]
		planned := map[Tunnel]bool{}
		for _, tunnel := range candidate.path {
			planned[tunnel] = true
		}
		extended := false
		for _, tunnel := range network.tunnels {
			if tunnel.valveRate == 0 || planned[tunnel] {
				continue
			}
			path := make([]Tunnel, len(candidate.path)+1)
			copy(path, candidate.path)
			path[len(path)-1] = tunnel
			estimate, doable := network.evaluatePath(path, TIME_LIMIT)
			if doable {
				newPlan := Plan{path: path, estimate: estimate}
				plans = helpers.SortedInsert(plans, newPlan, func(p Plan) int { return p.estimate })
				extended = true
			}
		}
		if !extended {
			bestPlan = candidate
			break
		}
	}
	return bestPlan.estimate
}

func (network Network) evaluatePath(path []Tunnel, timeTotal int) (int, bool) {
	/*
		Returns the heuristically adjusted value and whether it can be done
	*/
	distance := 0
	pressure := 0
	position := network.tunnels["AA"]
	visited := map[Tunnel]bool{position: true}
	for _, tunnel := range path {
		path := network.buildPath(position, tunnel)
		distance += len(path)
		if distance < timeTotal {
			pressure += tunnel.valveRate * (timeTotal - distance)
		} else {
			return 0, false
		}
		visited[tunnel] = true
		position = tunnel
	}
	for _, tunnel := range network.reverseSortedTunnels {
		if visited[tunnel] || tunnel.valveRate == 0 {
			continue
		}
		path := network.buildPath(position, tunnel)
		if distance+len(path) < timeTotal {
			pressure += tunnel.valveRate * (timeTotal - distance - len(path))
		}
	}
	return pressure, true
}

func buildNetwork(inputLines []string) Network {
	tunnels := map[string]Tunnel{}
	pendingConnections := map[Tunnel][]string{}
	for _, inputLine := range inputLines {
		tunnel, connectionStrings := lineToTunnel(inputLine)
		tunnels[tunnel.name] = tunnel
		pendingConnections[tunnel] = connectionStrings
	}
	connections := map[Tunnel][]Tunnel{}
	reverseSortedTunnels := []Tunnel{}
	for tunnel, names := range pendingConnections {
		connections[tunnel] = make([]Tunnel, len(names))
		for i, name := range names {
			connections[tunnel][i] = tunnels[name]
		}
		reverseSortedTunnels = helpers.SortedInsert(
			reverseSortedTunnels,
			tunnel,
			func(t Tunnel) int { return -t.valveRate },
		)
	}
	network := Network{
		connections:          connections,
		tunnels:              tunnels,
		reverseSortedTunnels: reverseSortedTunnels,
		paths:                map[[2]Tunnel][]Tunnel{},
	}
	return network
}

func lineToTunnel(inputLine string) (Tunnel, []string) {
	words := strings.Split(inputLine, " ")
	name := words[1]
	valveRate, err := strconv.Atoi(words[4][:len(words[4])-1][5:])
	if err != nil {
		log.Fatal(inputLine, words[4][:len(words[4])-1][5:])
	}
	connections := words[9:]
	for i, word := range connections {
		connections[i] = word[:2]
	}
	return Tunnel{name: name, valveRate: valveRate}, connections
}

type Tunnel struct {
	name      string
	valveRate int
}

type Network struct {
	connections          map[Tunnel][]Tunnel
	tunnels              map[string]Tunnel
	reverseSortedTunnels []Tunnel
	paths                map[[2]Tunnel][]Tunnel
}

type Plan struct {
	path     []Tunnel
	estimate int
}

func (network Network) buildPath(t1, t2 Tunnel) []Tunnel {
	cachedValue, isCached := network.paths[[2]Tunnel{t1, t2}]
	if isCached {
		return cachedValue
	}
	cachedValue, isCached = network.paths[[2]Tunnel{t2, t1}]
	if isCached {
		return cachedValue
	}

	paths := [][]Tunnel{{t1}}
	for !helpers.Any(paths, func(t []Tunnel) bool { return t[len(t)-1] == t2 }) {
		newPaths := [][]Tunnel{}
		for _, path := range paths {
			for _, nextStep := range network.connections[path[len(path)-1]] {
				if helpers.Any(path, func(t Tunnel) bool {
					return t == nextStep
				}) {
					continue
				}
				newPath := make([]Tunnel, len(path)+1)
				copy(newPath, path)
				newPath[len(newPath)-1] = nextStep
				newPaths = append(newPaths, newPath)
			}
		}
		paths = newPaths
	}
	var bestPath []Tunnel
	for _, path := range paths {
		if path[len(path)-1] == t2 {
			bestPath = path
			break
		}
	}

	network.paths[[2]Tunnel{t1, t2}] = bestPath
	return bestPath
}
