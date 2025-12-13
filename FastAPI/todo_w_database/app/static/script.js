const API_URL = "http://127.0.0.1:8000/todos";
let currentFilter = "all";

async function loadTodos() {
    const res = await fetch(API_URL);
    const todos = await res.json();

    const list = document.getElementById("todo-list");
    list.innerHTML = "";

    todos.forEach(todo => {

        //  VISIBILITY CONTROL
        if (currentFilter === "pending" && todo.is_completed) return;
        if (currentFilter === "completed" && !todo.is_completed) return;

        const li = document.createElement("li");
        li.className = "todo-item";

        if (todo.is_completed) {
            li.classList.add("completed");
        }

        li.innerHTML = `
            <label class="todo-left">
                <input 
                    type="checkbox"
                    ${todo.is_completed ? "checked" : ""}
                />
                <span>${todo.title}</span>
            </label>
            <button>×</button>
        `;

        // checkbox handler
        li.querySelector("input").addEventListener("change", e => {
            toggleTodo(todo.id, e.target.checked);
        });

        // delete handler
        li.querySelector("button").addEventListener("click", () => {
            deleteTodo(todo.id);
        });

        list.appendChild(li);
    });
}


async function toggleTodo(id, isCompleted) {
    await fetch(`${API_URL}/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_completed: isCompleted })
    });
    loadTodos();
}


document.getElementById("todo-form").addEventListener("submit", async e => {
    e.preventDefault(); /* normally when submit occurs page refreshes by using this we stop the page refreshing */

    const title = document.getElementById("title").value;

    await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
    });

    document.getElementById("title").value = "";
    loadTodos();
});


async function deleteTodo(id) {
    await fetch(`${API_URL}/${id}`, { method: "DELETE" });
    loadTodos();
}


document.querySelectorAll(".filters button").forEach(btn => {
    btn.addEventListener("click", () => {
        currentFilter = btn.dataset.filter;

        /* the below code is for highlighting the only button you clicked for css*/
        document.querySelectorAll(".filters button").forEach(b =>
            b.classList.remove("active")
        );

        btn.classList.add("active");
        loadTodos();
    });
});



loadTodos();