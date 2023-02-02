package day08

import (
	"strconv"
)

func Solve(inputLines []string) (int, int) {
	return partOne(inputLines), partTwo(inputLines)
}

func makeForest(inputLines []string) Forest {
	numRows := len(inputLines)
	numCols := len(inputLines[0])
	values := make([][]int, numRows)
	for j := range values {
		values[j] = make([]int, numCols)
	}
	for j, row := range inputLines {
		for i, treeRune := range row {
			values[j][i], _ = strconv.Atoi(string(treeRune))
		}
	}
	return Forest{numRows: numRows, numCols: numCols, values: values}
}

func partOne(inputLines []string) int {
	forest := makeForest(inputLines)

	visibleAddresses := map[Tree]bool{}
	for y := 0; y < forest.numRows; y++ {
		leftBlock, rightBlock := -1, -1
		leftTree, rightTree := -1, forest.numCols
		for leftTree < rightTree {
			if leftBlock < rightBlock {
				leftTree++
				height := forest.values[y][leftTree]
				if height > leftBlock {
					leftBlock = height
					visibleAddresses[Tree{y: y, x: leftTree, height: height}] = true
				}
			} else {
				rightTree--
				height := forest.values[y][rightTree]
				if height > rightBlock {
					rightBlock = height
					visibleAddresses[Tree{y: y, x: rightTree, height: height}] = true
				}
			}
		}
	}
	for x := 0; x < forest.numCols; x++ {
		topBlock, bottomBlock := -1, -1
		topTree, bottomTree := -1, forest.numRows
		for topTree < bottomTree {
			if topBlock < bottomBlock {
				topTree++
				height := forest.values[topTree][x]
				if height > topBlock {
					topBlock = height
					visibleAddresses[Tree{y: topTree, x: x, height: height}] = true
				}
			} else {
				bottomTree--
				height := forest.values[bottomTree][x]
				if height > bottomBlock {
					bottomBlock = height
					visibleAddresses[Tree{y: bottomTree, x: x, height: height}] = true
				}
			}
		}
	}

	return len(visibleAddresses)
}

func partTwo(inputLines []string) int {
	forest := makeForest(inputLines)

	bestScore := 0
	for y, row := range forest.values {
		for x := range row {
			score := forest.visibilityScore(y, x)
			if score > bestScore {
				bestScore = score
			}
		}
	}
	return bestScore
}

type Tree struct {
	y      int
	x      int
	height int
}

type Forest struct {
	numRows int
	numCols int
	values  [][]int
}

func (forest Forest) visibilityScore(y int, x int) int {
	height := forest.values[y][x]
	leftDistance := 0
	for dx := -1; x+dx >= 0; dx-- {
		leftDistance++
		if forest.values[y][x+dx] >= height {
			break
		}
	}
	rightDistance := 0
	for dx := 1; x+dx < forest.numCols; dx++ {
		rightDistance++
		if forest.values[y][x+dx] >= height {
			break
		}
	}
	topDistance := 0
	for dy := -1; y+dy >= 0; dy-- {
		topDistance++
		if forest.values[y+dy][x] >= height {
			break
		}
	}
	bottomDistance := 0
	for dy := 1; y+dy < forest.numRows; dy++ {
		bottomDistance++
		if forest.values[y+dy][x] >= height {
			break
		}
	}
	return leftDistance * rightDistance * topDistance * bottomDistance
}
