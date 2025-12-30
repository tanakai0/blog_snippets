from math import gcd

class Board:
    def __init__(self, m, n):
        """
        Attributes
        ----------
        m : int
            行数
        n : int
            列数
        full_mask : int
            盤面上の全点が未訪問状態(1)であることを表す bit を並べた整数
        lines : list[int]
            盤面上の「格子点を2点以上含む直線」を bitmask (Python int) で表したもののリスト
            bitmask での各ビットは盤面上の各点を id 順に並べたものに対応し、その交点は直線上にない(0)、その交点は直線上にある(1) を表す。
        """
        self.m = m
        self.n = n
        self.full_mask = (1 << (m * n)) - 1
        self.lines = self.enumerate_lines_bitmask(m, n)
        self.lines.sort(key=int.bit_count, reverse=True)
    def id2xy(self, id):
        return id // self.n, id % self.n
    def xy2id(self, x, y):
        return x * self.n + y
    def enumerate_lines_bitmask(self, m: int, n: int) -> list[int]:
        """
        m x n 格子上の「格子点を2点以上含む直線」を重複なく列挙し、
        各直線を bitmask (Python int) で返す。

        Board の番号付けに合わせる:
        id = x * n + y
        x in [0, m), y in [0, n)

        参考：[How to Find number of unique straight lines in a matrix - Stack Overflow](https://stackoverflow.com/questions/31772526/how-to-find-number-of-unique-straight-lines-in-a-matrix?utm_source=chatgpt.com)
        """

        def in_bounds(x: int, y: int) -> bool:
            return 0 <= x < m and 0 <= y < n

        lines: set[int] = set()

        # primitive 方向のみ（gcd(|dx|,|dy|)=1）、符号を正規化して片側だけ
        dirs: list[tuple[int, int]] = []
        for dy in range(-(n - 1), n):
            for dx in range(-(m - 1), m):
                if dx == 0 and dy == 0:
                    continue
                g = gcd(abs(dx), abs(dy))
                if g != 1:
                    continue  # primitive のみ
                # 反対向きの重複を避ける（dx>0 か、dx==0なら dy>0 のみ採用）
                if dx < 0 or (dx == 0 and dy < 0):
                    continue
                dirs.append((dx, dy))

        # 各方向について「始点だけ」から走査して重複排除
        # 直線の重複はまだあるため、set へ追加している
        # 重複している例： (dx, dy) = (0, 1) と (0, 2) は同じ直線を表す。
        for dx, dy in dirs:
            for x0 in range(m):
                for y0 in range(n):
                    # 1つ前が盤面内なら始点ではない（同じ直線を2回数えない）
                    px, py = x0 - dx, y0 - dy
                    if in_bounds(px, py):
                        continue

                    mask = 0
                    length = 0
                    x, y = x0, y0
                    while in_bounds(x, y):
                        mask |= 1 << self.xy2id(x, y)
                        length += 1
                        x += dx
                        y += dy

                    if length >= 2:
                        lines.add(mask)
        
        return list(lines)
    
def has_forced_win(m, n):
    """
    m×nの共線ゲームで、先手必勝かどうかを判定する。

    Parameters
    ----------
    m : int
        行
    n : int
        列

    Returns
    -------
    bool
        先手必勝かどうか
    """
    board = Board(m, n)
    FULL = board.full_mask
    lines = board.lines
    memo: dict[int, bool] = {}

    print("N points:", m*n)
    print("num lines:", len(board.lines))

    def win(state: int) -> bool:
        """
        現在の state (未訪問点の集合) から見て、次手番のプレイヤーが必勝かどうかを返す。

        Parameters
        ----------
        state : int
            訪問済み(0) / 未訪問(1) の点を bit で表した整数

        Returns
        -------
        _ : bool
            次手番のプレイヤーが必勝かどうか
        """
        if state == 0:
            return False  # 打つ手がないため、負け
        if state in memo:
            return memo[state]

        # どれか1手でも相手を負けにできれば勝ち
        for line in lines:
            # 未訪問かつ、line 上の点が一つもない場合
            if (state & line) == 0:
                continue
            next_state = state & (FULL ^ line)  # line 上の点を消す
            if not win(next_state):
                memo[state] = True
                return True

        memo[state] = False
        return False

    start = FULL
    result = win(start)
    print(f"{m}x{n}: {'first player wins' if result else 'second player wins'}")
    print("states computed:", len(memo))

if __name__ == "__main__":
    # 入力された m, n について先手必勝か判定
    m, n = int(input("m:")), int(input("n:")) 
    has_forced_win(m, n)
