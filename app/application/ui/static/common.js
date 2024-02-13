function toggleExpiresAtNumber() {
    const expires_dropdown = document.getElementById("expires_at_unit");
    let expires_input = document.getElementById("expires_at_number");
    expires_input.disabled = (expires_dropdown.value === "Never");
}
