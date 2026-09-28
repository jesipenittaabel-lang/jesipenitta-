async function parseError(response) {
    try {
        const data = await response.json();

        return (
            data.detail ||
            data.message ||
            "Request failed"
        );

    } catch {
        return "Request failed";
    }
}


function bindAuthForm(id, url) {
    const form = document.getElementById(id);

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const error =
                document.getElementById(
                    "formError"
                );

            error.textContent = "";

            const data = Object.fromEntries(
                new FormData(form)
            );

            try {

                const response =
                    await fetch(
                        url,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",
                            },

                            body: JSON.stringify(
                                data
                            ),
                        }
                    );

                if (!response.ok) {
                    throw new Error(
                        await parseError(response)
                    );
                }

                const output =
                    await response.json();

                location.href =
                    output.redirect ||
                    "/dashboard";

            } catch (errorObject) {

                error.textContent =
                    errorObject.message;
            }
        }
    );
}


function bindPlanner(
    id,
    url,
    mode
) {
    const form =
        document.getElementById(id);

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const result =
                document.getElementById(
                    "result"
                );

            result.innerHTML =
                '<div class="result-box">Generating your plan…</div>';

            let options = {
    method: "POST",
    credentials: "same-origin",
};


            if (mode === "json") {

                const raw =
                    Object.fromEntries(
                        new FormData(form)
                    );

                raw.budget =
                    Number(raw.budget);


                if (id === "homeForm") {

                    raw.rooms =
                        raw.rooms
                            .split(",")
                            .map(
                                x => x.trim()
                            )
                            .filter(Boolean);

                    raw.items =
                        raw.items
                            .split(",")
                            .map(
                                x => x.trim()
                            )
                            .filter(Boolean);
                }


                if (id === "partyForm") {
                    raw.guests =
                        Number(raw.guests);
                }


                options.headers = {
                    "Content-Type":
                        "application/json",
                };

                options.body =
                    JSON.stringify(raw);

            } else {

                options.body =
                    new FormData(form);
            }


            try {

                const response =
                    await fetch(
                        url,
                        options
                    );

                if (!response.ok) {
                    throw new Error(
                        await parseError(response)
                    );
                }

                const data =
                    await response.json();

function getProductImage(item) {
    const text = (
        (item.name || "") + " " +
        (item.category || "")
    ).toLowerCase();

    if (
        text.includes("light") ||
        text.includes("lamp") ||
        text.includes("lighting")
    ) {
        return "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80";
    }

    if (
        text.includes("fan") ||
        text.includes("cooling")
    ) {
        return "https://images.unsplash.com/photo-1631545806609-7c7c1a3e4a1d?auto=format&fit=crop&w=900&q=80";
    }

    if (
        text.includes("sofa") ||
        text.includes("chair") ||
        text.includes("table") ||
        text.includes("furniture")
    ) {
        return "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=900&q=80";
    }

    if (
        text.includes("wall") ||
        text.includes("decor") ||
        text.includes("art")
    ) {
        return "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=80";
    }

    return "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=900&q=80";
}


function renderResult(element, data) {

    const items = (data.items || [])
        .map(item => `
            <div class="rec-item">

                <img
                    class="rec-image"
                    src="${getProductImage(item)}"
                    alt="${escapeHtml(item.name)}"
                    loading="lazy"
                    onerror="this.style.display='none'"
                >

                <div class="rec-item-head">
                    <strong>
                        ${escapeHtml(item.name)}
                    </strong>

                    <strong>
                        ₹${Number(
                            item.estimated_price
                        ).toFixed(2)}
                    </strong>
                </div>

                <p>
                    ${escapeHtml(item.description)}
                </p>

                <span class="pill">
                    ${escapeHtml(item.category)}
                </span>

                <span class="pill">
                    ${escapeHtml(item.platform)}
                </span>

                <p>
                    <small>
                        ${escapeHtml(item.reason || "")}
                    </small>
                </p>

                ${
                    item.search_url &&
                    item.search_url !== "#"
                        ? `
                            <a
                                href="${escapeHtml(item.search_url)}"
                                target="_blank"
                                rel="noopener"
                            >
                                Search on
                                ${escapeHtml(item.platform)}
                                →
                            </a>
                        `
                        : ""
                }

            </div>
        `)
        .join("");

    element.innerHTML = `
        <div class="result-box">

            <div class="result-meta">
                <span class="pill">
                    ${escapeHtml(data.source)}
                </span>

                <span class="pill">
                    Budget ₹${Number(data.budget).toFixed(2)}
                </span>

                <span class="pill">
                    Remaining ₹${Number(data.remaining).toFixed(2)}
                </span>
            </div>

            <h2>
                ${escapeHtml(data.title)}
            </h2>

            <p>
                ${escapeHtml(data.summary)}
            </p>

            <div class="rec-grid">
                ${items}
            </div>

            <h3>
                Total allocated:
                ₹${Number(data.allocated_total).toFixed(2)}
            </h3>

            ${
                (data.tips || []).length
                    ? `
                        <h4>Tips</h4>
                        <ul>
                            ${data.tips.map(tip =>
                                `<li>${escapeHtml(tip)}</li>`
                            ).join("")}
                        </ul>
                    `
                    : ""
            }

        </div>
    `;
}
            } catch (errorObject) {

                result.innerHTML =
                    `<div class="result-box">
                        <p class="error">
                            ${escapeHtml(
                                errorObject.message
                            )}
                        </p>
                    </div>`;
            }
        }
    );
}


function escapeHtml(value) {

    return String(value).replace(
        /[&<>'"]/g,

        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "'": "&#39;",
            '"': "&quot;",
        }[character])
    );
}


function renderResult(
    element,
    data
) {

    const items =
        (data.items || [])
            .map(
                item => `
                <div class="rec-item">

                    <div class="rec-item-head">

                        <strong>
                            ${escapeHtml(
                                item.name
                            )}
                        </strong>

                        <strong>
                            ₹${Number(
                                item.estimated_price
                            ).toFixed(2)}
                        </strong>

                    </div>


                    <p>
                        ${escapeHtml(
                            item.description
                        )}
                    </p>


                    <span class="pill">
                        ${escapeHtml(
                            item.category
                        )}
                    </span>


                    <span class="pill">
                        ${escapeHtml(
                            item.platform
                        )}
                    </span>


                    <p>
                        <small>
                            ${escapeHtml(
                                item.reason || ""
                            )}
                        </small>
                    </p>


                    ${
                        item.search_url &&
                        item.search_url !== "#"

                            ? `
                            <a
                                href="${item.search_url}"
                                target="_blank"
                                rel="noopener"
                            >
                                Search on
                                ${escapeHtml(
                                    item.platform
                                )}
                                →
                            </a>
                            `

                            : ""
                    }

                </div>
                `
            )
            .join("");


    element.innerHTML = `
        <div class="result-box">

            <div class="result-meta">

                <span class="pill">
                    ${escapeHtml(
                        data.source
                    )}
                </span>

                <span class="pill">
                    Budget ₹${Number(
                        data.budget
                    ).toFixed(2)}
                </span>

                <span class="pill">
                    Remaining ₹${Number(
                        data.remaining
                    ).toFixed(2)}
                </span>

            </div>


            <h2>
                ${escapeHtml(
                    data.title
                )}
            </h2>


            <p>
                ${escapeHtml(
                    data.summary
                )}
            </p>


            ${items}


            <h3>
                Total allocated:
                ₹${Number(
                    data.allocated_total
                ).toFixed(2)}
            </h3>


            ${
                (data.tips || []).length

                    ? `
                        <h4>Tips</h4>

                        <ul>
                            ${data.tips
                                .map(
                                    tip =>
                                        `<li>
                                            ${escapeHtml(
                                                tip
                                            )}
                                        </li>`
                                )
                                .join("")}
                        </ul>
                    `

                    : ""
            }

        </div>
    `;
}