import chess
import chess.engine

STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

def score_to_cp(score, mate_cp=10000):
    if score.is_mate():
        return mate_cp if score.mate() > 0 else -mate_cp
    return score.score()

def position_complexity(engine, board, depth=18, top_n=4):
    #print("\n--- Analyzing position ---")
    #print(board)
    #print(f"Side to move: {'White' if board.turn else 'Black'}")

    info = engine.analyse(
        board,
        chess.engine.Limit(depth=depth),
        multipv=top_n
    )

    # Sort best → worst from side to move
    info.sort(
        key=lambda x: score_to_cp(x["score"].pov(board.turn)),
        reverse=True
    )

    evals = [
        score_to_cp(entry["score"].pov(board.turn))
        for entry in info
    ]

    best = evals[0]
    diffs = [abs(best - e) for e in evals[1:]]

    print("diffs",diffs)

    if len(evals) == 1:
        # only one legal move possible
        return 0

    avg_compl = sum(diffs) / len(diffs)
    if len(diffs) != 1 and avg_compl >= 500: # only one logical option exists
        print("skipping complexity analysis avg complexity beyond 500",avg_compl)
        return 0

    return avg_compl

def game_complexity_from_moves(moves_san, depth=12, top_n=3, start_move=5,end_move=40):
    board = chess.Board()
    complexities = []

    moves = moves_san.split()

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        for ply, san in enumerate(moves, start=1):
            print(f"\nPly {ply}: playing move {san}")
            try:
                board.push_san(san)
            except Exception as e:
                # Skip corrupted games
                print(f"Invalid move: {san}:{e}")
                return None

            # Skip opening (after move 10 = 20 plies)
            if ply < start_move * 2:
                print("Skipping opening phase","ply=",ply)
                continue

            if ply >= end_move * 2:
                break

            c = position_complexity(engine, board, depth, top_n)
            complexities.append(c)

    if not complexities:
        print("No positions analyzed.")
        return None

    compl = sum(complexities) / len(complexities)
    print(f"Final Game Complexity Calculated as: {compl:.1f} cp")


    return compl
