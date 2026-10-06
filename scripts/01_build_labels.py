"""Stage 1 (CPU, ~1 min): filter populations + construct bias labels from full data."""
from kbtp import data, bias

if __name__ == "__main__":
    print("== building populations ==")
    data.build_populations()
    print("== constructing bias labels ==")
    bias.build_bias()
    print("== stage 1 done ==")
