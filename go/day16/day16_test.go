package day16

import "testing"

func TestMutable(t *testing.T) {
	type Foo struct {
		name string
	}
	type FooNet struct {
		fooValues map[[2]Foo]int
	}
	addThing := func(fn FooNet, f1, f2 Foo) { fn.fooValues[[2]Foo{f1, f2}] = 1; return }
	type FooNetWrapper struct {
		fooNet FooNet
	}
	fn := FooNet{fooValues: map[[2]Foo]int{}}
	fnw1 := FooNetWrapper{fooNet: fn}
	fnw2 := FooNetWrapper{fooNet: fnw1.fooNet}
	addThing(fnw1.fooNet, Foo{"a"}, Foo{"b"})
	if len(fnw2.fooNet.fooValues) == 0 {
		t.Errorf("oops")
	}
	if fnw2.fooNet.fooValues[[2]Foo{{"a"}, {"b"}}] != 1 {
		t.Errorf("ugh")
	}
}
