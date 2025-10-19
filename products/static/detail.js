
function getCSRFToken(name) {
let cookieValue = null;
if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length) === name) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
}
return cookieValue;
}


let cartBtn = document.getElementById("cartBtn");
cartBtn.addEventListener("click", function () {
let id = this.dataset.product;
let action = this.dataset.action;
let url= this.dataset.url;
updateUserOrder(id, action, url);
});

const csrftoken = getCSRFToken("csrftoken");
console.log(csrftoken)

function updateUserOrder(productId, action, url) {
fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productId: productId, action: action }),
})
    .then((response) => {
        if (!response.ok) {
            alert(`Lỗi server: ${response.status}`);
            throw new Error(`Lỗi server: ${response.status}`);
        }
        alert("Thêm thành công vào giỏ hàng!!!");
        return response.json();
    })
    .then((data) => {
        console.log("data:", data);
    })
    .catch((error) => {
        console.error("Có lỗi:", error);
    });
}
