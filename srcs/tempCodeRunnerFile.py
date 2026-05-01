            maze.dfs()
            for row in maze.maze:
                print(" ".join(f"{cell:2}" for cell in row))