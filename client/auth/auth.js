module.exports.loggedIn = (req, res, next) => {
    if(req.session.loggedIn){
        next();
    } else{
        res.redirect('/login');
    }
}

module.exports.fee = (req, res, next) => {
    if(req.session.userfee){
        next();
    } else{
        res.redirect('/login');
    }
}