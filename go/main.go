package main

import (
	"adventOfCode2023/day01"
	"adventOfCode2023/day02"
	"adventOfCode2023/day03"
	"adventOfCode2023/day08"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"strings"
)

func main() {
	var day int
	flag.IntVar(&day, "day", 0, "puzzle day (1-25) (required)")
	var inputPath string
	flag.StringVar(&inputPath, "input", "", "path to puzzle input file (required)")
	flag.Parse()
	if inputPath == "" || day < 1 || day > 25 {
		flag.Usage()
		return
	}

	contents, err := ioutil.ReadFile(inputPath)
	if err != nil {
		log.Fatal(err)
	}
	inputLines := strings.Split(string(contents), "\n")
	if inputLines[len(inputLines)-1] == "" {
		inputLines = inputLines[:len(inputLines)-1]
	}

	switch day {
	case 1:
		fmt.Println(day01.Solve(inputLines))
	case 2:
		fmt.Println(day02.Solve(inputLines))
	case 3:
		fmt.Println(day03.Solve(inputLines))
	case 8:
		fmt.Println(day08.Solve(inputLines))
	default:
		fmt.Println("day not implemented yet")
	}
}
