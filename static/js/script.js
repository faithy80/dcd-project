function ConfirmMessage(type, id) {
    if (type == 'recipe') {
        if (confirm("Are you sure you want to delete this " + type + " ?")) {
            document.location.href = '/delete_recipe/' + id;
        }
    } else if (type == 'recipe category') {
        if (confirm("Are you sure you want to delete this " + type + " ?")) {
            if (confirm("ALL THE RECIPES IN THE CATEGORY WILL BE ALSO DELETED!")) {
                document.location.href = '/delete_recipe_category/' + id;
            }
        }
    }

}