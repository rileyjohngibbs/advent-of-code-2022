package helpers

func SliceEqual[T interface{}](left []T, right []T, eq func(T, T) bool) bool {
	if len(left) != len(right) {
		return false
	}
	for i := range left {
		if !eq(left[i], right[i]) {
			return false
		}
	}
	return true
}

func MapEqual[K comparable, V interface{}](left map[K]V, right map[K]V, eq func(V, V) bool) bool {
	if len(left) != len(right) {
		return false
	}
	for key, lValue := range left {
		rValue, exists := right[key]
		if !exists || !eq(lValue, rValue) {
			return false
		}
	}
	return true
}

func Any[T interface{}](slice []T, predicate func(T) bool) bool {
	for _, item := range slice {
		if predicate(item) {
			return true
		}
	}
	return false
}

func All[T interface{}](slice []T, predicate func(T) bool) bool {
	for _, item := range slice {
		if !predicate(item) {
			return false
		}
	}
	return true
}

func CopyMap[K comparable, V interface{}](src map[K]V) map[K]V {
	dst := make(map[K]V)
	for k, v := range src {
		dst[k] = v
	}
	return dst
}

func SliceSetEqual[T interface{}](left []T, right []T, eq func(T, T) bool) bool {
	if len(left) != len(right) {
		return false
	}
	return All(left, func(lt T) bool {
		return Any(right, func(rt T) bool {
			return eq(lt, rt)
		})
	})
}

func SortedInsert[E interface{}](es []E, e E, key func(E) int) []E {
	left, right := 0, len(es)
	eValue := key(e)
	index := (left + right) / 2
	for left < right {
		indexValue := key(es[index])
		if eValue == indexValue {
			left, right = index, index
		} else if eValue < indexValue {
			right = index
		} else {
			left = index + 1
		}
		index = (left + right) / 2
	}
	if index == len(es) {
		es = append(es, e)
	} else {
		es = append(es[:index+1], es[index:]...)
		es[index] = e
	}
	return es
}
