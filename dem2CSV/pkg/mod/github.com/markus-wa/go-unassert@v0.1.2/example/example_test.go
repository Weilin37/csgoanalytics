// +build !unassert_panic,!unassert_stderr,!unassert_test

package main

import (
	"testing"
)

func TestExample(t *testing.T) {
	main()
}
