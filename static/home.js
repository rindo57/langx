console.log('JS is running')
let languagesArr;
languagesArr = [
    'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German',
    'Khoisan', 'Korean', 'Swahili', 'Japanese', 'Russian', 'Arabic'
]

for (let i = 0; i < languagesArr.length; i++ ) {
    document.getElementById("user_languages").innerHTML(`<option>${languagesArr[i]}</option>`);
};

