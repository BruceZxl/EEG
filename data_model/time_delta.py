from typing import Optional

from loguru import logger


class TimeDelta:

    def __init__(self, *, hours=0, minutes=0, seconds=0, ms=0):
        smul = 1
        self.total_ms = 0
        self.hours = self.minutes = self.seconds = self.ms = 0
        for part, mul in zip(
                [ms, seconds, minutes, hours], [1, 1000, 60, 60]
        ):
            smul *= mul
            self.total_ms += int(part * smul)
        self.normalize()

    def normalize(self):
        res, self.ms = divmod(self.total_ms, 1000)
        res, self.seconds = divmod(res, 60)
        self.hours, self.minutes = divmod(res, 60)

    def to_readable(
            self, reference: Optional["TimeDelta"] = None, lang=None, truncate_lowers: bool = False):
        """
        To human-readable text.

        Examples:
         - 0:0.023 -> 23 ms
         - 2:16.200 -> 2 min 16.2 s
         - 2:16.234, reference=1:0:0 -> 0 hr 2 min 16.234 s
         - 2:16.234, reference=1:0:0, truncate_lowers=True -> 0 hr (you should mostly avoid this)
         - 2:16.234, reference=1:0:0.1, truncate_lowers=True -> 0 hr 2 min 16.2 s

        :param reference: Reference time delta to infer significance and precision from.
        :param lang: Language. reserved. Currently not used.
        :param truncate_lowers: Truncate the least significant parts if the reference has lower precision.
        :return: Human-readable string representation.
        """
        _ = lang
        units = ["时", "分", "秒", "毫秒"]
        idx_h, idx_min, idx_s, idx_ms = range(len(units))
        if reference is None:
            refs = [self]
        else:
            refs = [self, reference]
        refs = list(map(lambda t: [t.hours, t.minutes, t.seconds, t.ms], refs))
        # find largest and smallest non-zero parts e.g. hh:mm or mm:ss.ms
        starts, ends = idx_ms, idx_h
        for time in refs:
            finding_start = True
            for i, j in enumerate(time):
                if j != 0:
                    if finding_start:
                        starts = min(i, starts)
                        finding_start = False
                    ends = max(i, starts if truncate_lowers else ends)
        # if all zero then show "0 seconds"
        if starts > ends:
            starts = ends = idx_s
        desc, time = [], refs[0]
        # handle ms-only
        if starts == idx_ms:
            desc.append(str(time[idx_ms]))
            desc.append(units[idx_ms])
        else:
            # (if not ms-only) merge ms into s e.g. 1s200ms -> 1.2s, 2min0s110ms -> 2min0.11ms
            if ends == idx_ms:
                ms_ref = [refs[1]] if truncate_lowers and len(refs) > 1 else refs
                for i, j in zip([100, 10, 1], [1, 2, 3]):
                    if len([0 for ref in ms_ref if ref[idx_ms] % i != 0]) == 0:
                        ends = idx_s
                        time[idx_s] = f"{{:.{j}f}}".format(time[idx_s] + time[idx_ms] / 1000)
                        break
            for i in range(starts, ends + 1):
                desc.append(str(refs[0][i]))
                desc.append(units[i])
        return " ".join(desc)


def run_test(time, *, reference=None, ans):
    res = time.to_readable() if reference is None else time.to_readable(reference=reference)
    if ans is None:
        logger.info("Got {}.", res)
    elif ans == res:
        logger.info("Got {}, ok.", res)
    else:
        logger.error("Got {}, expecting {}.", res, ans)


if __name__ == '__main__':
    logger.info("running test")
    a = TimeDelta(hours=1)
    run_test(a, ans="1 时")
    b = TimeDelta(minutes=20, seconds=121)
    run_test(b, ans="22 分 1 秒")
    run_test(a, reference=b, ans="1 时 0 分 0 秒")
    a = TimeDelta(ms=100)
    run_test(a, ans="100 毫秒")
    run_test(a, reference=b, ans="0 分 0.1 秒")
    a = TimeDelta(ms=2220)
    run_test(a, reference=b, ans="0 分 2.22 秒")
