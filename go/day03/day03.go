package day03

import (
	"strings"
)

func Solve(inputLines []string) (int, int) {
	return partOne(inputLines), partTwo(inputLines)
}

func partOne(inputLines []string) int {
	prioritiesMap := priorities()
	prioritySum := 0
	for _, line := range inputLines {
		left := map[rune]int{}
		for i := 0; i < len(line)/2; i++ {
			char := rune(line[i])
			left[char] = 1
		}
		for i := len(line) / 2; i < len(line); i++ {
			char := rune(line[i])
			_, duplicate := left[char]
			if duplicate {
				prioritySum += prioritiesMap[char]
				break
			}
		}
	}
	return prioritySum
}

func partTwo(inputLines []string) int {
	prioritiesMap := priorities()
	prioritySum := 0
	for i := 0; i < len(inputLines); i += 3 {
		foundRunes := map[rune]int{}
		for _, r := range inputLines[i] {
			foundRunes[r] = 1
		}
		var commonRune rune
		for j := 1; j < 3; j++ {
			for _, r := range inputLines[i+j] {
				// fmt.Print(r, " ")
				count, exists := foundRunes[r]
				if exists && count == j {
					foundRunes[r] = count + 1
				}
				if foundRunes[r] == 3 {
					commonRune = r
					break
				}
			}
		}
		prioritySum += prioritiesMap[commonRune]
	}
	return prioritySum
}

func priorities() map[rune]int {
	pri := map[rune]int{}
	alphas := "abcdefghijklmnopqrstuvwxyz"
	for i, a := range "abcdefghijklmnopqrstuvwxyz" {
		pri[a] = i + 1
	}
	for i, A := range strings.ToUpper(alphas) {
		pri[A] = i + 27
	}
	return pri
}
