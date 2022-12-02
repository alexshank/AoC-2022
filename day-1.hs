import System.IO

main = do
  handle <- openFile "day-1-input.txt" ReadMode
  contents <- hGetContents handle
  putStr contents
  hClose handle
  return contents


// once I understand Haskell better, I can use this (probably bad) way of getting the input text
// then we can mess around in the interactive REPL
ghci> :l day-1.hs
ghci> temp :: String <- main
ghci> temp
ghci> lines contents // at this point, have a list of strings and are ready to solve!



