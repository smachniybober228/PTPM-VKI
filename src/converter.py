class Converter:
    @staticmethod
    def do(x: float) -> int:
        # x ∈ [100.7; +∞)
        if x >= 100.7:
            return 1000

        # x ∈ (0; 100.7)
        if x > 0:
            return int(x)

        # x == 0.0
        if x == 0.0:
            raise ValueError("x не может быть равен 0")

        # x ∈ [-30.4; 0)
        if x >= -30.4:
            return int(x) - 5

        # x ∈ (-∞; -30.5]
        return -2000