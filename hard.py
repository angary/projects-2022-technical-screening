"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge. 
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
import json
import re

UOC = 6

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    
    # TODO: COMPLETE THIS FUNCTION!!!
    reqs = clean_reqs(CONDITIONS[target_course])
    return eval_reqs(reqs, courses_list)


def clean_reqs(reqs: str) -> str:
    res = re.sub(r" +", " ", reqs.upper())
    res = res.split(":")[-1].strip()
    res = re.sub(r"^(\d{4})", "COMP$1", res)
    res = res.replace("COMPLETION OF ", "")
    return res


def eval_reqs(reqs: str, courses_list: list) -> bool:
    # Cleaning
    reqs = reqs.strip()

    # Recursive modification
    if "(" in reqs: # Sliding window to find 1 level nested strings in brackets
        l, r, brackets_found = 0, 0, 0
        for i, c in enumerate(reqs):
            if c == "(":
                if brackets_found == 0:
                    l = i
                brackets_found += 1
            elif c == ")":
                if brackets_found == 1:
                    r = i
                brackets_found -= 1
            if r != 0 and brackets_found == 0:
                mid = reqs[l+1:r]
                if "OR" in mid or "AND" in mid: # Eval to True or False
                    reqs = reqs.replace(f"({mid})", str(eval_reqs(mid, courses_list)))
                elif "," in mid: # Eval set of courses to num achieved courses
                    req_courses = set([x.strip() for x in mid.split(",")])
                    count = len(req_courses.intersection(courses_list))
                    reqs = reqs.replace(f"({mid})", str(count))
                r = 0
    if "UNITS" in reqs: # Eval to num achieved courses
        if "LEVEL" in reqs: # X UOC in a level X courses
            level_and_faculty = re.search(r"LEVEL (\d) ([A-Z]{4})", reqs)
            level, faculty = level_and_faculty.group(0).split()[-2:]
            has = len(list(filter(lambda x: f"{faculty}{level}" in x, courses_list)))
            reqs = reqs.replace(f"LEVEL {level} {faculty} COURSES", str(has))
        elif "COURSES" in reqs: # X UOC in courses of a faculty
            faculty = re.search(r"IN ([A-Z]{4})", reqs).group(1)
            has = len(list(filter(lambda x: faculty in x, courses_list)))
            reqs = reqs.replace(f"{faculty} COURSES", str(has))
        else: # X UOC in anything
            reqs += f" IN {len(courses_list)}"
    
    # Recursive evaluation
    if "OR" in reqs:
        return any([eval_reqs(x, courses_list) for x in reqs.split("OR")])
    if "AND" in reqs:
        return all([eval_reqs(x, courses_list) for x in reqs.split("AND")])
    
    # Base cases
    if "UNITS" in reqs:
        needs = int(re.match(r"\d+", reqs).group(0))
        has = int(re.search(r"IN +(\d+)", reqs).group(1))
        return has >= (needs // UOC)
    if reqs in ("True", "False"):
        return eval(reqs)
    if not reqs:
        return True
    return reqs in courses_list


if __name__ == "__main__":
    print(is_unlocked(["COMP1911"], "COMP1521"), "== True")
    print(is_unlocked([], "COMP1521"), "== False")
    print(is_unlocked(["COMP1531", "COMP2521"], "COMP2511"), "== True")
    print(is_unlocked(["COMP1531", "COMP1927"], "COMP2511"), "== True")
    print(is_unlocked(["COMP1531", "COMP1927", "COMP2521"], "COMP2511"), "== True")
    print(is_unlocked(["COMP1927", "COMP2521"], "COMP2511"), "== False")
    print(is_unlocked(["COMP1927"], "COMP3151"), "== True")
    print(is_unlocked(["COMP1521", "COMP2521"], "COMP3151"), "== True")
    print(is_unlocked(["DPST1092", "COMP2521"], "COMP3151"), "== True")
    print(is_unlocked(["COMP2521"], "COMP3151"), "== False")
    print(is_unlocked(["COMP1521", "DPST1092"], "COMP3151"), "== False")
    print(is_unlocked(["COMP6443", "COMP1511"], "COMP9301"), "== False")
    print(is_unlocked(["COMP6443", "COMP6843", "COMP1511"], "COMP9301"), "== True")
    print(is_unlocked(["COMP1511", "COMP1521", "COMP2521", "COMP2511", "COMP2121"], "COMP3901"), "== True")
    print(is_unlocked(["COMP1927", "COMP2521"], "COMP9302"), "== False")
    print(is_unlocked(["COMP1927", "COMP2521"], "COMP4161"), "== False")
