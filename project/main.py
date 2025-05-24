import multiprocessing
from run_simulation import run_simulation, interpret_results, run_ml
from tables import make_results_table
from areas import areas
from tqdm import tqdm


def wrapper(args):
    return interpret_results(*args)
    # return run_simulation(*args)


def main() -> None:
    tasks = [
        (DB, neighborhood)
        for DB, neighborhoods in areas.items()
        for neighborhood in neighborhoods
    ]
    num_threads = multiprocessing.cpu_count()

    with multiprocessing.Pool(num_threads) as pool:
        results = list(tqdm(pool.imap(wrapper, tasks), total=len(tasks)))

    # final_results = dict(results)
    # make_results_table(final_results)
    #
    # run_ml()


if __name__ == "__main__":
    main()
