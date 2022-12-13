import java.io.File
import java.util.LinkedList

// data classes give us proper equality checks for free
data class Coord(val x: Int, val y: Int)

fun main() {
    // get input grid and dimensions
    val grid: List<List<Int>> = parseInput(System.getProperty("user.dir") + "/inputs/day-12-input.txt")
    val m: Int = grid.size
    val n: Int = grid[0].size

    // pad around grid so we can ignore edge conditions
    val integers: List<List<Int>> = grid.map { listOf(1000) + it + listOf(1000) }
    val padded: List<List<Int>> = listOf(List(n + 2) { 1000 }) + integers + listOf(List(n + 2) { 1000 })

    val start: Coord = Coord(20 + 1, 0 + 1) // found from the cursor position in my IDE :)
    val end: Coord = Coord(20 + 1, 112 + 1)

    // part 1
    println(breadthFirstSearch(padded, start, end)!!.size - 1)

    // part 2
    val results = mutableListOf<List<Coord>>()
    for (j in 0 until m) {
        for (i in 0 until n) {
            if (grid.get(j).get(i) == 'a'.code) {
                val dist = breadthFirstSearch(padded, Coord(j + 1, i + 1), end)
                dist?.let { results.add(it) }
            }
        }
    }
    println(results.map { it.size - 1 }.min())
}

// returns a shortest path to the desired coord, or nothing if no path exists
fun breadthFirstSearch(padded: List<List<Int>>, start: Coord, end: Coord): List<Coord>? {
    val seen = mutableSetOf<Coord>()
    val queue = LinkedList<List<Coord>>()
    queue.add(listOf<Coord>(start))

    while (queue.size > 0) {
        val currentPath: List<Coord> = queue.remove()
        val current: Coord = currentPath.last()
        
        if (current == end) { return currentPath }

        listOf(
            Coord(current.x - 1, current.y),
            Coord(current.x + 1, current.y),
            Coord(current.x, current.y - 1),
            Coord(current.x, current.y + 1)
        ).filter {
            !seen.contains(it) && current.canClimbTo(padded, it)
        }.forEach {
            seen.add(it)
            queue.add(currentPath + listOf(it))
        }
    }

    return null
}

fun Coord.canClimbTo(padded: List<List<Int>>, destination: Coord): Boolean =
    padded.get(this.x).get(this.y) + 1 >= padded.get(destination.x).get(destination.y)

// TODO we can't find the indices of S and E if we immediately map to ints
fun parseInput(fileName: String): List<List<Int>> = File(fileName).readLines().map {
    line -> line.map { it -> characterToElevation(it) }
}

fun characterToElevation(c: Char): Int =
    when (c) {
        'S' -> 'a'.code
        'E' -> 'z'.code
        else -> c.code
    }
