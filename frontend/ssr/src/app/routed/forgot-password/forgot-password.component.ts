import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material';
import { Subscription } from 'rxjs';
import { GetDataService } from '../../services/get-data.service';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.scss']
})
export class ForgotPasswordComponent implements OnInit {

  private subscription: Subscription;
  public id: string;
  public newPassword1: string;
  public newPassword2: string;
  public errorClass: string;

  constructor(
    private router: Router,
    private activateRoute: ActivatedRoute,
    private getDataService: GetDataService,
    public snackBar: MatSnackBar
  ) {
    this.subscription = activateRoute.params.subscribe(params => {
      this.id = params['id'];
    });
   }

  ngOnInit() {
    if (this.id) {
      this.errorClass = '';
    }
  }

  save() {
    if (!this.newPassword1 || !this.newPassword2 || (this.newPassword1 != this.newPassword2)) {
      this.snackBar.open('Проверьте введенные данные!', 'x', {
        duration: 3000
      });
      this.errorClass = 'invalid';
    } else {
      if (this.id) {
        this.getDataService.setNewPassword(this.id, this.newPassword1).subscribe((data) => {
          if (data) {
            this.snackBar.open(data.message, 'x', {
              duration: 3000
            });
            this.router.navigate(['']);
          }
        }, (error) => {
          this.snackBar.open(error.error.message, 'x', {
            duration: 3000
          });
        });
      }
    }
  }

  setClass() {
    if (!this.newPassword1 || !this.newPassword2 || (this.newPassword1 != this.newPassword2)) {
      this.errorClass = 'invalid';
    } else {
      this.errorClass = 'valid';
    }
  }

}
