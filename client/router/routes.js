const { response } = require('express');
var express = require('express');
var api = require('../api/api');
const auth = require('../auth/auth');

var router = express.Router();

var message = "";
var warn = false;

router.get('/login', function (req, res) {
    if(req.session.loggedIn){
        res.redirect('/');
    }else{
        res.render('login');
    }
})

router.post('/login', (req,res,next) => {
    username = req.body.username;
    password = req.body.password;
    api.login(username, password).then(function(response){
        if(response.data.code > 0){
            res.locals.user = response.data.user
            next();
        } else{
            res.redirect('/login');
        }
    })
},
(req, res) => {
    req.session.loggedIn = true;
    req.session.user = res.locals.user;
    res.redirect('/');
})

router.get('/', auth.loggedIn,function (req, res) {
    res.render('index', {user: req.session.user, warn: warn, message: message})
})

router.get('/fee', auth.loggedIn, (req, res, next) => {
    id = req.query.id
    api.fee(id).then((response) => {
        if(response.data.available > 0){
            message = "";
            req.session.userfee = response.data.student;
            next();
        }else{
            warn = true;
            message = response.data.message
            res.redirect('/');
        }
    })
},
(req, res) => {
    res.render('fee', {user: req.session.user, userfee: req.session.userfee});
})

router.get('/otp', auth.fee,(req, res) => {
    res.render('otp', {user: req.session.user, userfee: req.session.userfee, message: message, warn: warn});
})

router.post('/otp', (req, res, next) => {
    iduser = req.session.user[0];
    idfee = req.session.userfee[0];
    if(parseInt(req.session.user[6]) - parseInt(req.session.userfee[2]) >= 0){
        api.check(idfee, iduser).then((response) => {
            if(response.data.data.length < 1 || (response.data.data[0] == req.session.user[0] && response.data.data[1] == req.session.userfee[0])){
                message = "";
                next();
            }else{
                warn = true;
                message = "MSSV này đang được thanh toán bởi tài khoản khác";
                res.redirect('/');
            }
        })
    } else{
        warn = true;
        message = "Số dư của bạn không đủ để thanh toán học phí";
        res.redirect('/')
    }
},
(req, res) => {
    email = req.session.user[5];
    api.otp(iduser, idfee, email).then((response) => {
        res.redirect('/otp');
    })
})

router.post('/transaction',(req, res) => {
    otp = req.body.otp;
    reba = parseInt(req.session.user[6]) - parseInt(req.session.userfee[2]);
    api.transaction(otp, reba).then((response) => {
        message = response.data.message;
        if(response.data.code > 0){
            warn = false;
            api.user(req.session.user[0]).then((response) => {
                req.session.user = response.data.user;
                res.redirect('/');
            })
        }else{
            warn = true;
            res.redirect('/otp');
        }
    })
})

router.get('/sendagainotp', auth.fee, (req, res) => {
    iduser = req.session.user[0];
    idfee = req.session.userfee[0];
    email = req.session.user[5];
    warn = false;
    message = "Mã OTP đã được gửi lại!"
    api.otp(iduser, idfee, email).then((response) => {
        res.redirect('/otp');
    })
})

router.get('/logout', (req, res) => {

    req.session.destroy(function(err) {
        // cannot access session here
    });

    res.redirect('/login');
})

module.exports = router;