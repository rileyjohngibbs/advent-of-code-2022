package main

import (
	"adventOfCode2023/day01"
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

	switch day {
	case 1:
		fmt.Println(day01.Solution(inputLines))
	default:
		fmt.Println("day not implemented yet")
	}
}
