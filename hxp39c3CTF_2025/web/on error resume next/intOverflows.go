package main
import (
	"math"
	"fmt"
)
  
/*
minInt64: -9223372036854775808
maxInt64: 9223372036854775807
maxUint64: 18446744073709551615
*/
  
func main() {
	// int64 min/max
	minInt64 := int64(math.MinInt64)
	maxInt64 := int64(math.MaxInt64)
	  
	// uint64 max
	maxUint64 := uint64(math.MaxUint64)
	  
	fmt.Println("minInt64: ", minInt64)
	fmt.Println("maxInt64: ", maxInt64)
	fmt.Println("maxUint64: ", maxUint64)
}