import System.IO
import Data.List

main = do
  inputData <- readFile "day-1-input.txt"
  let inputLines = lines inputData

  -- create list of tuples containing sublist ranges (add boundary indices)
  let enumeratedLines = zip [0..] inputLines
  let blankIndices = [-1] ++ [fst x | x <- enumeratedLines, null (snd x)] ++ [length inputLines]
  let adjIndices = zipAdj blankIndices

  -- create list of sublists, then reduce each sublist to its sum
  let subLists = [slice (fst x + 1) (snd x) inputLines | x <- adjIndices]
  let sums = [sum (map strToInt xs) | xs <- subLists]

  -- part 1
  print $ maximum sums

  -- part 2 (sum the last 3 elements of sorted array)
  let sumCount = length sums
  print $ sum $ slice (sumCount - 3) sumCount $ sort sums
  -- ($) :: (a -> b) -> a -> b
  -- the above is same as: print (sum (slice (sumCount - 3) sumCount (sort sums)))
  
-- take [1,2,3] and create [(1,2), (2,3)]
zipAdj :: [a] -> [(a, a)]
zipAdj xs = zip xs (tail xs)

-- basically python's slicing functionality xs[from:to]
slice :: Int -> Int -> [a] -> [a]
slice from to xs = take (to - from) (drop from xs)

-- we need to convert to Int (sum undefined for String)
strToInt :: String -> Int
strToInt str = read str::Int
