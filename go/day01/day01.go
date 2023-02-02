package day01

import (
	"strconv"
)

func Solve(inputLines []string) (int, int) {
	return partOne(inputLines), partTwo(inputLines)
}

func partOne(inputLines []string) int {
	maxCalories := 0
	currentCalories := 0

	for _, line := range inputLines {
		if line == "" {
			if currentCalories > maxCalories {
				maxCalories = currentCalories
			}
			currentCalories = 0
		} else {
			calories, _ := strconv.Atoi(line)
			currentCalories += calories
		}
	}

	return maxCalories
}

func partTwo(inputLines []string) int {
	maxCaloriesArray := [3]int{0, 0, 0}
	currentCalories := 0

	for _, line := range inputLines {
		if line == "" {
			for i, cal := range maxCaloriesArray {
				if currentCalories > cal {
					maxCaloriesArray[i] = currentCalories
					currentCalories = cal
				}
			}
			currentCalories = 0
		} else {
			calories, _ := strconv.Atoi(line)
			currentCalories += calories
		}
	}

	total := 0
	for _, cal := range maxCaloriesArray {
		total += cal
	}
	return total
}
