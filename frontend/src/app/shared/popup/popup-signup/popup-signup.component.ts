import { Component, OnInit } from '@angular/core';
import { MatDialogRef, MatSnackBar } from '@angular/material';
import { Router } from '@angular/router';
import { GetDataService } from '../../services/get-data.service';
import { AppDataService } from '../../services/app-data.service';

@Component({
  selector: 'app-popup-signup',
  templateUrl: './popup-signup.component.html',
  styleUrls: ['./popup-signup.component.scss']
})
export class PopupSignupComponent implements OnInit {

  public agree = true;
  public username: string;
  public email: string;
  public password: string;
  public password2: string;
  public phone: string;
  public showError = false;
  public errorText = '';
  public errors = {
    name: false,
    email: false,
    phone: false,
    password1: false,
  };

  constructor(
    public dialogRef: MatDialogRef<PopupSignupComponent>,
    private getDataService: GetDataService,
    private router: Router,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit() {
  }

  closePopup(res: string = '') {
    this.dialogRef.close(res);
  }

  checkPhone() {
    if (!this.phone) {
      this.phone = '+7';
    }
  }

  signUp() {
    for (let k in this.errors) {
      if (k) {
        this.errors[k] = false;
      }
    }
    if (this.username.length < 6){
      this.errorText = 'Неверно указано ФИО';
      this.errors.name = true;
      this.showError = true;
      return;
    } else {
      this.errorText = '';
      this.showError = false;
      this.errors.name = false;
    }
    let fioArray = this.username.split(' ');
    if (fioArray.length < 2) {
      this.errorText = 'Неверно указано ФИО';
      this.errors.name = true;
      this.showError = true;
      return;
    } else {
      this.errorText = '';
      this.showError = false;
    }
    let lastName = fioArray[0];
    let firstName = fioArray[1];
    let secondName = undefined;
    if (fioArray.length > 2) {
      secondName = fioArray[2];
    }
    if (this.password != this.password2) {
      this.errorText = 'Пароли не совпадают!';
      this.showError = true;
    } else {
      this.errorText = '';
      this.showError = false;
    }
    this.getDataService.signUpUser(this.email, this.email, this.password, this.password2, lastName, firstName, secondName, this.phone).subscribe((data) => {
      // console.log(data);
      if (data.token && data.user) {
        AppDataService.user = data.user;
        AppDataService.userToken = 'JWT ' + data.token;
        localStorage.removeItem('bshop_id');
        localStorage.removeItem('bshop_t');
        localStorage.setItem('bshop_id', data.user.id);
        localStorage.setItem('bshop_t', AppDataService.userToken);
        AppDataService.userLoggedIn = true;
        AppDataService.userStatusChange$.emit();
        this.router.navigate(['account']);
        this.closePopup();
      }
    }, (error) => {
      let msg = '';
      if (error.error) {
        for (let key in error.error) {
          if (key) {
            msg += error.error[key] + '\r\n';
            this.errors[key] = true;
          }
        }
      }
      if (!msg) {
        msg = 'Ошибка регистрации!';
      }
      this.snackBar.open(msg, 'x', {
        duration: 3500
      })
    })
  }

  openDoc() {
    window.open('/assets/docs/dogovor.pdf', '_blank');
  }

}
