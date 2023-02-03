package day12

import (
	"sort"
)

func Solve(inputLines []string) (int, int) {
	return partOneBeta(inputLines), partTwoBeta(inputLines)
}

type Address struct {
	y int
	x int
}

func (addr Address) neighbors(height int, width int) []Address {
	neighbors := []Address{}
	for _, vector := range [][2]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}} {
		address := Address{y: addr.y + vector[0], x: addr.x + vector[1]}
		if address.y >= 0 && address.y < height && address.x >= 0 && address.x < width {
			neighbors = append(neighbors, address)
		}
	}
	return neighbors
}

type Path struct {
	visited map[Address]bool
	head    Address
}

func (path Path) length() int {
	return len(path.visited)
}

func (path Path) heuristic(d Address) int {
	return path.length() + manhattan(path.head, d)
}

func manhattan(a Address, b Address) int {
	return absDiff(a.x, b.x) + absDiff(a.y, b.y)
}

func absDiff(a int, b int) int {
	if a > b {
		return a - b
	}
	return b - a
}

func (path Path) extend(heightmap map[Address]int) []Path {
	neighbors := []Address{}
	headHeight := heightmap[path.head]
	for _, vector := range [][2]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}} {
		neighbor := Address{y: path.head.y + vector[0], x: path.head.x + vector[1]}
		stepHeight, validAddress := heightmap[neighbor]
		if validAddress && !path.visited[neighbor] && stepHeight <= headHeight+1 {
			neighbors = append(neighbors, neighbor)
		}
	}
	paths := []Path{}
	for _, neighbor := range neighbors {
		newVisited := map[Address]bool{}
		for address := range path.visited {
			newVisited[address] = true
		}
		newVisited[neighbor] = true
		paths = append(paths, Path{head: neighbor, visited: newVisited})
	}
	return paths
}

func makeElevationMap(inputLines []string) map[Address]int {
	letterToInt := map[rune]int{'S': 0, 'E': 25}
	for h, letter := range "abcdefghijklmnopqrstuvwxyz" {
		letterToInt[letter] = h
	}
	elevationMap := map[Address]int{}
	for y, row := range inputLines {
		for x, letter := range row {
			elevationMap[Address{y: y, x: x}] = letterToInt[letter]
		}
	}
	return elevationMap
}

// This is really slow
func partOne(inputLines []string) int {
	elevationMap := makeElevationMap(inputLines)

	startingPoint := Address{y: -1, x: -1}
	destination := Address{y: -1, x: -1}
	for y, row := range inputLines {
		for x, letter := range row {
			if letter == 'S' {
				startingPoint = Address{y: y, x: x}
			} else if letter == 'E' {
				destination = Address{y: y, x: x}
			}
			if startingPoint.x != -1 && destination.x != -1 {
				break
			}
		}
		if startingPoint.x != -1 && destination.x != -1 {
			break
		}
	}

	paths := []Path{}
	paths = append(paths, Path{
		visited: map[Address]bool{startingPoint: true},
		head:    startingPoint,
	})
	visited := map[Address]int{startingPoint: 0}
	return pathfind(paths, visited, destination, elevationMap)
}

// This is really slow
func partTwo(inputLines []string) int {
	elevationMap := makeElevationMap(inputLines)

	startingPoints := []Address{}
	destination := Address{y: -1, x: -1}
	for y, row := range inputLines {
		for x, letter := range row {
			if letter == 'S' || letter == 'a' {
				startingPoints = append(startingPoints, Address{y: y, x: x})
			} else if letter == 'E' {
				destination = Address{y: y, x: x}
			}
		}
	}

	paths := []Path{}
	visited := map[Address]int{}
	for _, start := range startingPoints {
		paths = append(paths, Path{visited: map[Address]bool{start: true}, head: start})
		visited[start] = 0
	}
	return pathfind(paths, visited, destination, elevationMap)
}

func pathfind(
	paths []Path,
	visited map[Address]int,
	destination Address,
	elevationMap map[Address]int,
) int {
	var completedPathLength int
	solved := false
	for !solved {
		sort.Slice(paths, func(i, j int) bool {
			return paths[i].heuristic(destination) > paths[j].heuristic(destination)
		})
		candidate := paths[len(paths)-1]
		paths = paths[:len(paths)-1]
		newPaths := candidate.extend(elevationMap)
		for _, newPath := range newPaths {
			shortestDistance, preVisited := visited[newPath.head]
			if preVisited && shortestDistance <= newPath.length() {
				continue
			}
			visited[newPath.head] = candidate.length()
			if newPath.head == destination {
				solved = true
				completedPathLength = candidate.length()
				break
			} else {
				paths = append(paths, newPath)
			}
		}
	}
	return completedPathLength
}

// This is much faster
func partOneBeta(inputLines []string) int {
	elevationMap := makeElevationMap(inputLines)
	height := len(inputLines)
	width := len(inputLines[0])

	startingPoint := Address{y: -1, x: -1}
	destination := Address{y: -1, x: -1}
	for y, row := range inputLines {
		for x, letter := range row {
			if letter == 'S' {
				startingPoint = Address{y: y, x: x}
			} else if letter == 'E' {
				destination = Address{y: y, x: x}
			}
			if startingPoint.x != -1 && destination.x != -1 {
				break
			}
		}
		if startingPoint.x != -1 && destination.x != -1 {
			break
		}
	}

	frontier := map[Address]bool{startingPoint: true}
	visited := map[Address]bool{startingPoint: true}
	return pathfindBeta(frontier, visited, destination, elevationMap, height, width)
}

// This is much faster
func partTwoBeta(inputLines []string) int {
	elevationMap := makeElevationMap(inputLines)
	height := len(inputLines)
	width := len(inputLines[0])

	startingPoints := []Address{}
	destination := Address{y: -1, x: -1}
	for y, row := range inputLines {
		for x, letter := range row {
			if letter == 'S' || letter == 'a' {
				startingPoints = append(startingPoints, Address{y: y, x: x})
			} else if letter == 'E' {
				destination = Address{y: y, x: x}
			}
		}
	}

	frontier := map[Address]bool{}
	visited := map[Address]bool{}
	for _, startingPoint := range startingPoints {
		frontier[startingPoint] = true
		visited[startingPoint] = true
	}
	return pathfindBeta(frontier, visited, destination, elevationMap, height, width)
}

func pathfindBeta(
	frontier map[Address]bool,
	visited map[Address]bool,
	destination Address,
	elevationMap map[Address]int,
	height int,
	width int,
) int {
	steps := 0
	for !visited[destination] {
		newFrontier := map[Address]bool{}
		for addr := range frontier {
			elevation := elevationMap[addr]
			for _, neighbor := range addr.neighbors(height, width) {
				if !visited[neighbor] && elevationMap[neighbor] <= elevation+1 {
					newFrontier[neighbor] = true
					visited[neighbor] = true
				}
			}
		}
		frontier = newFrontier
		steps++
	}
	return steps
}
