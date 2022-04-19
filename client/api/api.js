const axios = require('axios');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname,'../../.env') })


module.exports.login = async function(username, password){
    return await axios.post( process.env.URL_API +'/login',{
        username: username,
        password: password
    });
};

module.exports.user = function(iduser){
    return axios.post( process.env.URL_API +'/user',{
        id_user: iduser
    });
}

module.exports.fee = function(ID){
    return axios.post( process.env.URL_API +'/fee',{
        ID: ID
    });
}

module.exports.check = function(idfee, iduser){
    return axios.post( process.env.URL_API +'/checking',{
        id_fee: idfee,
        id_user: iduser
    });
}

module.exports.otp = function(iduser, idfee, email) {
    return axios.post( process.env.URL_API +'/otp',{
        id_user: iduser,
        id_fee: idfee,
        email: email
    });
}

module.exports.transaction = function(otp, reba) {
    return axios.post( process.env.URL_API +'/transaction',{
        otp: otp,
        reba: reba
    });
}