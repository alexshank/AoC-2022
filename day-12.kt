import java.io.File
import java.util.LinkedList

fun main() {
    // get input grid and dimensions
    val grid: List<List<Int>> = parseInput(System.getProperty("user.dir") + "/inputs/day-12-input.txt")
    val y_max: Int = grid.size
    val x_max: Int = grid[0].size

    // pad around grid so we can ignore edge conditions
    val paddingRow = List(x_max) { 1000 }
    val paddedGrid: List<List<Int>> =
        (listOf(paddingRow) + grid + listOf(paddingRow)).map { listOf(1000) + it + listOf(1000) }

    val start: Coord = Coord(20 + 1, 0 + 1) // found from the cursor position in my IDE :)
    val end: Coord = Coord(20 + 1, 112 + 1)

    // part 1 (we know !! is safe here)
    println(breadthFirstSearch(paddedGrid, start, end)!!.size - 1)

    // TODO clever solution: You can just run BFS from the destination and have it terminate
    // TODO when it reaches ANY square that could have been a start square
    // part 2
    val results = mutableListOf<List<Coord>>()
    for (y in 0 until y_max) {
        for (x in 0 until x_max) {
            if (grid[y][x] == 'a'.code) {
                val shortestPath = breadthFirstSearch(paddedGrid, Coord(y + 1, x + 1), end)
                shortestPath?.let { results.add(it) }
            }
        }
    }
    println(results.map { it.size - 1 }.min())
}

// returns a shortest path to the desired coord, or null if no path exists
private fun breadthFirstSearch(paddedGrid: List<List<Int>>, start: Coord, end: Coord): List<Coord>? {
    val seen = mutableSetOf<Coord>()
    val queue = LinkedList<List<Coord>>()
    queue.add(listOf<Coord>(start))

    while (queue.size > 0) {
        val currentPath: List<Coord> = queue.remove()
        val current: Coord = currentPath.last()
        
        if (current == end) { return currentPath }

        current.candidateList().filter {
            !seen.contains(it) && current.canClimbTo(paddedGrid, it)
        }.forEach {
            seen.add(it)
            queue.add(currentPath + listOf(it))
        }
    }

    return null
}

// data classes give us proper equality checks for free
private data class Coord(val x: Int, val y: Int)

private fun Coord.candidateList(): List<Coord> = listOf(
        Coord(this.x - 1, this.y),
        Coord(this.x + 1, this.y),
        Coord(this.x, this.y - 1),
        Coord(this.x, this.y + 1)
    )

private fun Coord.canClimbTo(paddedGrid: List<List<Int>>, destination: Coord): Boolean =
    paddedGrid[this.x][this.y] + 1 >= paddedGrid[destination.x][destination.y]

private fun parseInput(fileName: String): List<List<Int>> = File(fileName).readLines().map {
    line -> line.map { it -> characterToElevation(it) }
}

private fun characterToElevation(c: Char): Int =
    when (c) {
        'S' -> 'a'.code
        'E' -> 'z'.code
        else -> c.code
    }
