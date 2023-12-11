async function show_ingredients() {
    let space = document.getElementById("SPA")
    space.innerHTML = "<h1>Składniki</h1>"

    await fetch("/static/ingredients.html")
        .then(resp => resp.text())
        .then(html => {
            space.innerHTML += html
        })
        .catch(err => {
            console.warn('Failed to fetch page: ', err);
        });

    let table = document.getElementById("ingredients_tbody")

    fetch("/api/ingredients")
        .then(resp => {
            if (resp.status == 200)
                return resp.json();
        })
        .then(data => {
            if (data.length > 0) table.innerHTML = ""
            for (let i = 0; i < data.length; i++) {
                table.innerHTML += `<tr><td><a onclick="show_dish_with_ing(this)">${data[i]}</a></td></tr>`
            }
        })
        .catch(err => {
            console.warn('Failed to fetch data: ', err);
        });
}

async function show_dish_with_ing(event) {
    let ingredient = event.innerText
    let space = document.getElementById("SPA")

    space.innerHTML = `<h1>Dania wykorzystujące składnik: ${ingredient}</h1>`

    await fetch("/static/dishes.html")
        .then(resp => resp.text())
        .then(html => {
            space.innerHTML += html
        })
        .catch(err => {
            console.warn('Failed to fetch page: ', err);
        });

    let table = document.getElementById("dishes_tbody")

    fetch(`/api/ingredients/${ingredient.replace(/ /g, "_")}`)
        .then(resp => {
            if (resp.status == 200)
                return resp.json();
        })
        .then(data => {
            if (data.length > 0) table.innerHTML = ""
            for (let i = 0; i < data.length; i++) {
                table.innerHTML +=
                    `<tr>
                        <td><a onclick="show_dish(this)">${data[i].name}</a></td>
                        <td>${data[i].types}</td>
                    </tr>`
            }
        })
        .catch(err => {
            console.warn('Failed to fetch data: ', err);
        });
}

async function show_dish(event) {
    let dish = event.innerText
    let space = document.getElementById("SPA")

    space.innerHTML = `<h1>Danie: ${dish}</h1>`

    await fetch("/static/dish.html")
        .then(resp => resp.text())
        .then(html => {
            space.innerHTML += html
        })
        .catch(err => {
            console.warn('Failed to fetch page: ', err);
        });

    let button = document.getElementById("delete_button")
    button.addEventListener("click", delete_dish(dish))

    let subdishes = document.getElementById("subdishes_tbody")
    let ingredients = document.getElementById("ingredients_tbody")
    let dishes = document.getElementById("dishes_tbody")

    fetch(`/api/dishes/${dish.replace(/ /g, "_")}`)
        .then(resp => {
            if (resp.status == 200)
                return resp.json();
        })
        .then(data => {
            if (data.subdishes.length > 0) subdishes.innerHTML = ""
            for (let i = 0; i < data.subdishes.length; i++) {
                subdishes.innerHTML +=
                    `<tr>
                        <td><a onclick="show_dish(this)">${data.subdishes[i]}</a></td>
                    </tr>`
            }

            if (data.ingredients.length > 0) ingredients.innerHTML = ""
            for (let i = 0; i < data.ingredients.length; i++) {
                ingredients.innerHTML +=
                    `<tr>
                        <td><a onclick="show_dish_with_ing(this)">${data.ingredients[i]}</a></td>
                    </tr>`
            }

            if (data.in_dishes.length > 0) dishes.innerHTML = ""
            for (let i = 0; i < data.in_dishes.length; i++) {
                dishes.innerHTML +=
                    `<tr>
                        <td><a onclick="show_dish(this)">${data.in_dishes[i]}</a></td>
                    </tr>`
            }
        })
        .catch(err => {
            console.warn('Failed to fetch data: ', err);
        });
}

async function show_add() {
    let space = document.getElementById("SPA")
    space.innerHTML = "<h1>Dodaj do bazy</h1>"

    await fetch("/static/add.html")
        .then(resp => resp.text())
        .then(html => {
            space.innerHTML += html
        })
        .catch(err => {
            console.warn('Failed to fetch page: ', err);
        });
}

async function save(event) {
    console.log(event)
    event.tagName
    const childs = event.children
    let dish = {
        subdishes: [],
        ingredients: []
    }
    for (let i = 0; i < childs.length; i++) {
        element = childs[i]
        if (element.tagName === "INPUT" && element.value.trim() !== "") {
            element.value = element.value.trim()
            if (element.name === "dish")
                dish.name = element.value
            if (element.name === "type")
                dish.type = element.value
            if (element.name === "ingredient")
                dish.ingredients.push(element.value)
            if (element.name === "subdishes")
                dish.subdishes.push(element.value)
        }
    }

    if (dish.name === undefined)
        alert("Nazwa dania jest wymagana")
    return

    await fetch("/api/dishes", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dish)
    })
        .catch(err => {
            console.warn('Failed to post data: ', err);
        });

    this.innerText = dish.name
    show_dish(this)
}

function more_fields(event) {
    const previous = event.previousElementSibling.previousElementSibling

    const newElement = previous.insertAdjacentElement("afterend", previous.cloneNode())
    newElement.value = ""
    previous.insertAdjacentHTML("afterend", "<br>")
}

function delete_dish(dish_name) {
    return () => {
        console.log(dish_name)
        fetch(`/api/dishes/${dish_name.replace(/ /g, "_")}`, {
            method: "DELETE"
        })
            .then(resp => {
                show_ingredients()
            })
            .catch(err => {
                console.warn('Failed to fetch data: ', err);
            });
    }
}
