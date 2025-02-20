from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    session,
)

import pandas as pd

app = Flask(__name__)

car = pd.read_csv("car_data.csv", sep=",", encoding="utf-8")
car_df = pd.DataFrame(car)


@app.route("/")
def initial():
    return render_template("initial.html")


@app.route("/find", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        selected_categories = request.form.getlist("category")
        selected_areas = request.form.getlist("area")
        selected_colors = request.form.getlist("color")
        min_price = request.form.get("min_price", "")
        max_price = request.form.get("max_price", "")
        start_year = request.form.get("start_year", "")
        end_year = request.form.get("end_year", "")

        if len(selected_categories) == 26:
            selected_categories.pop()
        if len(selected_areas) == 18:
            selected_areas.pop()
        if len(selected_colors) == 13:
            selected_colors.pop()

        temp_df = pd.DataFrame(columns=car_df.columns)
        filter_df = car_df.copy()
        filter_df["가격"] = (
            filter_df["가격"].str.replace(",", "").str.replace("만원", "").astype(int)
        )
        filter_df["연식"] = (
            filter_df["연식"].str.extract(r"\((\d{2})년형\)").astype(int)
        )
        filter_df["연식"] = filter_df["연식"].apply(
            lambda x: x + 1900 if x >= 90 else x + 2000
        )

        if selected_categories or selected_areas or selected_colors:
            condition = pd.Series(True, index=filter_df.index)

            if selected_categories:
                condition &= filter_df["모델명"].str.contains(
                    "|".join(selected_categories)
                )

            if selected_areas:
                condition &= filter_df["지역"].str.contains("|".join(selected_areas))

            if selected_colors:
                condition &= filter_df["색상"].str.contains("|".join(selected_colors))

            temp_df = filter_df[condition]

        final_df = temp_df.copy()
        if len(final_df) == 0:
            # 가격 범위 필터링
            if min_price.isdigit() and max_price.isdigit():
                final_df = filter_df[
                    (filter_df["가격"] >= int(min_price))
                    & (filter_df["가격"] <= int(max_price))
                ]

            if start_year.isdigit() and end_year.isdigit():
                final_df = filter_df[
                    (filter_df["연식"] >= int(start_year))
                    & (filter_df["연식"] <= int(end_year))
                ]

        else:
            if min_price.isdigit() and max_price.isdigit():
                final_df = final_df[
                    (final_df["가격"] >= int(min_price))
                    & (final_df["가격"] <= int(max_price))
                ]

            if start_year.isdigit() and end_year.isdigit():
                final_df = final_df[
                    (final_df["연식"] >= int(start_year))
                    & (final_df["연식"] <= int(end_year))
                ]

        if len(selected_categories) == 25:
            selected_categories = ["전체"]
        if len(selected_areas) == 17:
            selected_areas = ["전체"]
        if len(selected_colors) == 12:
            selected_colors = ["전체"]

        return render_template(
            "home.html",
            data=final_df.to_dict(orient="records"),
            model=selected_categories,
            area=selected_areas,
            color=selected_colors,
            minp=min_price,
            maxp=max_price,
            s_year=start_year,
            e_year=end_year,
        )

    return render_template("home.html", data=None)
