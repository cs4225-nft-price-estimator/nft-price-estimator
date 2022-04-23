const development_url = 'http://127.0.0.1:5000/api/estimate'

async function upload_image(image) {
    console.log("Upload and classify called!");
    const data = await fetch(development_url, {
        method: 'POST',
        body: JSON.stringify({"image_b64": image}),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(async (response) => {
        const res = await response.json();
        return res;
    }).catch((err) => {
        console.log(err);
    });
    const res_b64 = data['classified_b64'];
    let estimated_price = 0;
    try {
        estimated_price = parseFloat(data['price']);
    } catch (e) {
        estimated_price = "Error predicting price, contact admin"
    }
    const innerHTML = `<p><h2> Result: </h2></p>
                <img src="data:image/png;base64,${res_b64}" alt="Classified Image">
                <p><h5> Estimated Price: ${estimated_price} ETH </h3><p>`;
    document.getElementById('predictedImage').innerHTML = innerHTML;
    document.getElementById('hasUploaded1').remove();
    document.getElementById('hasUploaded2').remove();
    $('#loadingModal').modal("hide");
}