import multiprocessing

import ujson
from areas import areas
from run_simulation import interpret_results, run_ml
from tables import make_results_tables
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

    final_results = dict(results)
    with open("final_results.json", "w") as f:
        ujson.dump(final_results, f)
    make_results_tables()

    run_ml()


if __name__ == "__main__":
    main()
