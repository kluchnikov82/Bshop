import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { MatDialogRef } from '@angular/material';
import { isNullOrUndefined } from 'util';
import { GetDataService } from '../../../services/get-data.service';

@Component({
  selector: 'app-popup-address',
  templateUrl: './popup-address.component.html',
  styleUrls: ['./popup-address.component.scss']
})
export class PopupAddressComponent implements OnInit {

  userDataForm = new FormGroup({
    fioControl: new FormControl('', [Validators.required, Validators.minLength(6), Validators.pattern(/[А-Я][а-я]{0,}\s[А-Я][а-я]{1,}/)]),
    phoneControl: new FormControl('', [Validators.required, Validators.minLength(16)]),
    emailControl: new FormControl('', [Validators.required, Validators.email])
  });

  deliveryForm = new FormGroup({
    regionControl: new FormControl(),
    cityControl: new FormControl(),
    streetControl: new FormControl(),
    houseControl: new FormControl(),
    flatControl: new FormControl()
  });

  kladrId: string;
  postcode: string;

  public regionOptions: string[] = [];
  private oldRegion: any;
  public cityOptions: string[] = [];
  private oldCity: any;
  public streetOptions: string[] = [];
  private oldStreet: any;
  public houseOptions: string[] = [];
  private oldHouse: any;
  private location: any;
  private selectedSuggestion: any;
  private unrestrictedAddress = '';

  constructor(
    private getDataService: GetDataService,
    public dialogRef: MatDialogRef<PopupAddressComponent>,
  ) { }

  ngOnInit() {
    this.location = {};
    let regionControl = this.deliveryForm.get('regionControl');
    regionControl.valueChanges.subscribe(() => {
      if (regionControl.value) {
        if (regionControl.value.length > 2) {
          this.regionOptions = [];
          let queryDaData = {
            locations: [],
            from_bound: {value: 'region'},
            to_bound: {value: 'area'},
            query: regionControl.value
          };
          this.autocompleteAddress(regionControl, queryDaData, this.oldRegion, this.regionOptions);
          this.eraseAddressControls(['cityControl', 'streetControl', 'houseControl', 'flatControl']);
          this.cityOptions = [];
          this.streetOptions = [];
          this.houseOptions = [];
        }
      }
    });

    let cityControl = this.deliveryForm.get('cityControl');
    cityControl.valueChanges.subscribe(() => {
      if (cityControl.value) {
        if (cityControl.value.length > 1) {
          this.cityOptions = [];
          let locations = [];
          locations.push(this.location);
          let queryDaData = {
            locations: locations,
            from_bound: {value: 'city'},
            to_bound: {value: 'settlement'},
            query: cityControl.value
          };
          this.autocompleteAddress(cityControl, queryDaData, this.oldCity, this.cityOptions);
          this.eraseAddressControls(['streetControl', 'houseControl', 'flatControl']);
          this.streetOptions = [];
          this.houseOptions = [];
        }
      }
    });

    let streetControl = this.deliveryForm.get('streetControl');
    streetControl.valueChanges.subscribe(() => {
      if (streetControl.value) {
        if (streetControl.value.length) {
          this.streetOptions = [];
          let locations = [];
          locations.push(this.location);
          let queryDaData = {
            locations: locations,
            from_bound: {value: 'street'},
            to_bound: {value: 'street'},
            query: streetControl.value
          };
          this.autocompleteAddress(streetControl, queryDaData, this.oldStreet, this.streetOptions);
          this.eraseAddressControls(['houseControl', 'flatControl']);
          this.houseOptions = [];
        }
      }
    });

    let houseControl = this.deliveryForm.get('houseControl');
    houseControl.valueChanges.subscribe(() => {
      if (houseControl.value) {
        if (houseControl.value.length) {
          this.houseOptions = [];
          let locations = [];
          locations.push(this.location);
          let queryDaData = {
            locations: locations,
            from_bound: {value: 'house'},
            query: houseControl.value
          };
          this.autocompleteAddress(houseControl, queryDaData, this.oldHouse, this.houseOptions);
          this.eraseAddressControls(['flatControl']);
        }
      }
    });
  }

  autocompleteAddress(control: AbstractControl, query: any, oldValue: any, options: string[]) {
    let dadataTimeout = setTimeout(() => {
      if (control.value == oldValue) {
        clearTimeout(dadataTimeout);
      } else {
        oldValue = control.value;
        this.getDataService.dadataQuery('62c868493b7000c72a320298458761611b70cc31', query).subscribe((data) => {
          // console.log(data);
          if (data.suggestions) {
            if (data.suggestions.length) {
              data.suggestions.forEach(suggest => {
                options.push(suggest);
              });
            }
          }
        });
      }
    }, 500);
  }

  eraseAddressControls(arrayControls: string[]) {
    for (let controlName of arrayControls) {
      this.deliveryForm.get(controlName).setValue('');
    }
  }

  selectRegion(event) {
    let region = event.option.value;
    this.location = {};

    // console.log(event);
    if (region) {
      if (region.data.area_fias_id) {
        this.location['area_fias_id'] = region.data.area_fias_id;
      } else {
        this.location['region_fias_id'] = region.data.region_fias_id;
      }
    }
  }

  selectCity(event) {
    let city = event.option.value;
    this.location['settlement_fias_id'] = '';
    this.location['city_fias_id'] = '';
    // this.eraseAddressControls(['streetControl','houseControl','flatControl'], [this.streetOptions, this.houseOptions]);
    if (city) {
      if (city.data.settlement_fias_id) {
        this.location['settlement_fias_id'] = city.data.settlement_fias_id;
      } else {
        this.location['city_fias_id'] = city.data.city_fias_id;
      }
      this.kladrId = city.data.kladr_id;
      this.postcode = city.data.postal_code;
      this.selectedSuggestion = city.data;
      this.unrestrictedAddress = city.unrestricted_value;
    }
  }

  selectStreet(event) {
    let street = event.option.value;
    this.location['street_fias_id'] = '';
    // this.eraseAddressControls(['houseControl','flatControl'], [this.houseOptions]);
    if (street) {
      this.location['street_fias_id'] = street.data.street_fias_id;
      this.kladrId = street.data.kladr_id;
      this.postcode = street.data.postal_code;
      this.selectedSuggestion = street.data;
      this.unrestrictedAddress = street.unrestricted_value;
      if (!this.postcode) {
        this.getDataService.dadataQuery('62c868493b7000c72a320298458761611b70cc31',
          {
            query: this.unrestrictedAddress,
            restrict_value: true,
            count: 1
          }).subscribe((data) => {
            if (data.suggestions) {
              if (data.suggestions.length == 1) {
                this.selectedSuggestion = data.suggestions[0].data;
                this.postcode = this.selectedSuggestion.postal_code;
              }
            }
        });
      }
    }
  }

  selectHouse(event) {
    let house = event.option.value;
    // this.eraseAddressControls(['flatControl'], []);
    if (house) {
      this.kladrId = house.data.kladr_id;
      this.postcode = house.data.postal_code;
      this.selectedSuggestion = house.data;
      this.unrestrictedAddress = house.unrestricted_value;
      if (!this.postcode) {
        this.getDataService.dadataQuery('62c868493b7000c72a320298458761611b70cc31',
          {
            query: this.unrestrictedAddress,
            restrict_value: true,
            count: 1
          }).subscribe((data) => {
            if (data.suggestions) {
              if (data.suggestions.length == 1) {
                this.selectedSuggestion = data.suggestions[0].data;
                this.postcode = this.selectedSuggestion.postal_code;
              }
            }
        });
      }
    }
  }

  displayRegion(region?: any) {
    return region ? region.value : '';
  }

  displayCity(city? : any) {
    if (city) {
      let area = isNullOrUndefined(city.data.area_with_type) ? '' : city.data.area_with_type + ', ';
      let cityA = isNullOrUndefined(city.data.city_with_type) ? '' : city.data.city_with_type + ', ';
      let settlement = isNullOrUndefined(city.data.settlement_with_type) ? '' : city.data.settlement_with_type;
      let fullCity = (area + cityA + settlement).trim();
      if (fullCity.substr(fullCity.length - 1, 1) == ',') {
        fullCity = fullCity.substring(0, fullCity.length - 1);
      }
      return fullCity;
    } else {
      return '';
    }
  }

  displayStreet(street?: any) {
    if (street) {
      let adr = '';
      if (street.data.settlement && street.data.area) {
        adr = street.data.street_with_type + '(' + street.data.settlement_with_type + ', ' + street.data.area_with_type + ')';
      } else {
        adr = street.data.street_with_type;
      }
      return adr;
    } else {
      return '';
    }
  }

  displayHouse(house?: any) {
    if (house) {
      let adr = house.data.house_type + ' ' + house.data.house;
      if (house.data.block) {
        adr += ' ' + house.data.block_type + ' ' + house.data.block;
      }
      return adr;
    } else {
      return '';
    }
  }

  saveAddress() {
    let address = {
      kladr_id: this.kladrId,
      postcode: this.selectedSuggestion.postal_code,
      region: this.selectedSuggestion.region_with_type,
      district: this.selectedSuggestion.area_with_type,
      settlement: this.selectedSuggestion.settlement_with_type,
      country: this.selectedSuggestion.country,
      city: this.selectedSuggestion.city_with_type,
      street: this.selectedSuggestion.street_with_type,
      house: this.selectedSuggestion.house,
      cdek_city_id: null
    };

    this.dialogRef.close(address);
  }

}
