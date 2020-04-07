function ConfirmMessage(type, URL) {
    if (confirm("Are you sure you want to delete this " + type + " ?")) {
        document.location.href = URL;
    }
}