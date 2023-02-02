package day02

import "strings"

func Solve(inputLines []string) (int, int) {
	return partOne(inputLines), partTwo(inputLines)
}

func partOne(inputLines []string) int {
	score := 0

	for _, line := range inputLines {
		moves := strings.Split(line, " ")

		var opponent Move
		switch moves[0] {
		case "A":
			opponent = Rock
		case "B":
			opponent = Paper
		default:
			opponent = Scissors
		}

		var player Move
		switch moves[1] {
		case "X":
			player = Rock
		case "Y":
			player = Paper
		default:
			player = Scissors
		}

		outcome := determineOutcome(player, opponent)
		score += int(outcome) + int(player)
	}

	return score
}

func partTwo(inputLines []string) int {
	score := 0

	for _, line := range inputLines {
		moves := strings.Split(line, " ")

		var opponent Move
		switch moves[0] {
		case "A":
			opponent = Rock
		case "B":
			opponent = Paper
		default:
			opponent = Scissors
		}

		var outcome Outcome
		switch moves[1] {
		case "X":
			outcome = Lose
		case "Y":
			outcome = Draw
		default:
			outcome = Win
		}

		player := determineMove(opponent, outcome)
		score += int(outcome) + int(player)
	}

	return score
}

type Move int

const (
	Rock     Move = 1
	Paper         = 2
	Scissors      = 3
)

type Outcome int

const (
	Win  Outcome = 6
	Lose         = 0
	Draw         = 3
)

func determineOutcome(player Move, opponent Move) Outcome {
	if player == opponent {
		return Draw
	}
	switch player {
	case Rock:
		if opponent == Scissors {
			return Win
		} else {
			return Lose
		}
	case Paper:
		if opponent == Rock {
			return Win
		} else {
			return Lose
		}
	default: // Scissors
		if opponent == Paper {
			return Win
		} else {
			return Lose
		}
	}
}

func determineMove(opponent Move, outcome Outcome) Move {
	switch outcome {
	case Win:
		switch opponent {
		case Rock:
			return Paper
		case Paper:
			return Scissors
		default: // Scissors
			return Rock
		}
	case Lose:
		switch opponent {
		case Rock:
			return Scissors
		case Paper:
			return Rock
		default: // Scissors
			return Paper
		}
	default:
		return opponent
	}
}
