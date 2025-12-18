const API_URL = "http://127.0.0.1:8000/todos";
let currentFilter = "all";
let isRegisterMode = false;


const loginSection = document.getElementById("login-section");
const todoSection = document.getElementById("todo-section");
const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

function getToken() {
  return localStorage.getItem("token");
}

function showLogin() {
  loginSection.style.display = "block";
  todoSection.style.display = "none";
}

function showTodos() {
  loginSection.style.display = "none";
  todoSection.style.display = "block";
}


const toggleBtn = document.getElementById("toggle-auth");
const authTitle = document.getElementById("auth-title");
const authBtn = document.getElementById("auth-btn");
const toggleText = document.getElementById("toggle-text");

function toggleAuthMode() {
  isRegisterMode = !isRegisterMode;
  loginError.textContent = "";

  if (isRegisterMode) {
    authTitle.textContent = "Register";
    authBtn.textContent = "Register";
    toggleText.textContent = "Already have an account?";
    toggleBtn.textContent = "Login";
  } else {
    authTitle.textContent = "Login";
    authBtn.textContent = "Login";
    toggleText.textContent = "Don’t have an account?";
    toggleBtn.textContent = "Register";
  }
}

toggleBtn.addEventListener("click", toggleAuthMode);


loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (isRegisterMode) {
    // REGISTER
    const res = await fetch("/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      loginError.textContent = "Registration failed (email may already exist)";
      return;
    }

    loginError.style.color = "green";
    loginError.textContent = "Registered successfully. You can now login.";
    toggleAuthMode(); // switch back to login
    return;
  }

  // LOGIN
  const res = await fetch("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      username: email,
      password: password
    })
  });

  if (!res.ok) {
    loginError.style.color = "red";
    loginError.textContent = "Invalid email or password";
    return;
  }

  const data = await res.json();
  localStorage.setItem("token", data.access_token);

  loginError.textContent = "";
  showTodos();
  loadTodos();
});




const logoutBtn = document.getElementById("logout-btn");
logoutBtn.addEventListener("click" , () => {
    localStorage.removeItem("token");
    showLogin();
});

async function loadTodos() {
    const res = await fetch(API_URL ,{
        headers : {
            "Authorization": `Bearer ${getToken()}`
        } 
    });
    if (res.status === 401){
        localStorage.removeItem("token")
        showLogin();
        return;
    }

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

/* Update the todo as completed or not */ 
async function toggleTodo(id, isCompleted) {
    await fetch(`${API_URL}/${id}`, {
        method: "PUT",
        headers: { 
            "Content-Type" : "application/json",
            "Authorization" : `Bearer ${getToken()}`
        },
        body: JSON.stringify({ is_completed : isCompleted })
    });
    loadTodos();
}

/* Create Todo */
document.getElementById("todo-form").addEventListener("submit", async e => {
    e.preventDefault(); /* normally when submit occurs page refreshes by using this we stop the page refreshing */

    const title = document.getElementById("title").value;

    await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization" : `Bearer ${getToken()}`
        },
        body: JSON.stringify({ title })
    });

    document.getElementById("title").value = "";
    loadTodos();
});

/* Delete Todo */
async function deleteTodo(id) {
    await fetch(`${API_URL}/${id}`,{
        method: "DELETE" ,
        headers : {
            "Authorization" : `Bearer ${getToken()}`
        }
    });
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


if (getToken()) {
    showTodos();
    loadTodos();
} else {
    showLogin();
}
