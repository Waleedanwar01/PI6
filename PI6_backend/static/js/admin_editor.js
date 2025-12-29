document.addEventListener("DOMContentLoaded", function() {
    // Check if tinymce is loaded
    var checkTinyMCE = setInterval(function() {
        if (typeof tinymce !== "undefined") {
            clearInterval(checkTinyMCE);
            tinymce.init({
                selector: '#id_content',
                height: 500,
                menubar: true,
                plugins: [
                    'advlist autolink lists link image charmap print preview anchor',
                    'searchreplace visualblocks code fullscreen',
                    'insertdatetime media table paste code help wordcount'
                ],
                toolbar: 'undo redo | formatselect | ' +
                'bold italic backcolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | help',
                content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
            });
        }
    }, 100);
});
