import System.IO

main = do
  inputData <- readFile "inputs/day-6-input.txt"
  let inputLine = head (lines inputData)
  print (partOne inputLine)
  -- let inputLine = take 1 lines
  -- print (inputLine)

-- recursion is no bueno for this (problem gets bigger)
partOne :: (Num t) => String -> t
partOne [] = 0
partOne (x:xs) = z + partOne xs
  where z = 1 if 