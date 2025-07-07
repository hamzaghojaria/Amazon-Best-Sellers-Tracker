const categoryColors = {};

function getRandomPastelColor() {
  const hue = Math.floor(Math.random() * 360);
  return `hsl(${hue}, 70%, 85%)`;
}

function applyCategoryColors() {
  document.querySelectorAll(".category-btn").forEach(btn => {
    const cat = btn.getAttribute("data-category");
    if (!categoryColors[cat]) {
      categoryColors[cat] = getRandomPastelColor();
    }

    btn.style.backgroundColor = categoryColors[cat];
    btn.style.color = "#333";
  });
}

function highlightActiveCategory(activeBtn) {
  document.querySelectorAll(".category-btn").forEach(btn => {
    btn.classList.remove("active");
    const cat = btn.getAttribute("data-category");
    btn.style.backgroundColor = categoryColors[cat];
    btn.style.color = "#333";
  });

  const activeCat = activeBtn.getAttribute("data-category");
  activeBtn.classList.add("active");
  activeBtn.style.backgroundColor = categoryColors[activeCat].replace("85%", "65%");
  activeBtn.style.color = "#fff";
}

document.addEventListener("DOMContentLoaded", () => {
  applyCategoryColors();

  const categoryButtons = document.querySelectorAll(".category-btn");

  categoryButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      highlightActiveCategory(btn);
      const selectedCategory = btn.getAttribute("data-category");
      loadProducts(selectedCategory);
    });
  });

  // Highlight default & load products
  const defaultBtn = document.querySelector(".category-btn.active") || categoryButtons[0];
  highlightActiveCategory(defaultBtn);
  loadProducts(defaultBtn.getAttribute("data-category"));
});

async function loadProducts(category) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.classList.add("fade-out");

  setTimeout(async () => {
    resultsDiv.innerHTML = "Loading...";

    try {
      const res = await fetch(`/api/bestsellers/${category}`);
      const data = await res.json();
      resultsDiv.innerHTML = "";

      data.forEach((product, index) => {
        const tagColor = categoryColors[category] || "#007bff";

        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
          <div class="rank-badge">#${index + 1}</div>
          <div class="category-tag" style="background: ${tagColor}; font-weight: 700;">
            ${category.toUpperCase()}
          </div>
          <img src="${product.image}" alt="${product.title}">
          <h4>${product.title}</h4>
          <span class="price-tag">${product.price}</span>
          <p><strong>Rating:</strong> ${product.rating !== "N/A" ? `⭐ ${product.rating}` : "No rating"}</p>
          <a href="${product.link}" target="_blank"><strong>View Product</strong> →</a>
        `;
        resultsDiv.appendChild(card); // ✅ Ensure cards are added
      });

    } catch (err) {
      resultsDiv.innerHTML = "Failed to load products.";
      console.error(err);
    }

    resultsDiv.classList.remove("fade-out");
  }, 200);
}

// Back to Top Button Logic
const backToTopBtn = document.getElementById("backToTop");

window.addEventListener("scroll", () => {
  if (window.scrollY > 300) {
    backToTopBtn.classList.add("show");
  } else {
    backToTopBtn.classList.remove("show");
  }
});

backToTopBtn?.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});
